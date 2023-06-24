import random
from typing import List
from agents.threadCachingAgent import ThreadCachingAgent
from spade.message import Message
from spade.template import Template
from spade.behaviour import (
    FSMBehaviour,
    State,
    PeriodicBehaviour,
    CyclicBehaviour,
    OneShotBehaviour,
)
from messageTemplates.yellowPagesAgentTemplates import (
    CraneRegistrationMsgBody,
    REGISTER_AGREE_TEMPLATE,
    REGISTER_REFUSE_TEMPLATE,
    SERVICES_LIST_INFORM_TEMPLATE,
    TranstainerListRequestMsgBody,
)
from messageTemplates.basicTemplates import BLOCK_TEMPLATE
from messageTemplates.containerArrivalTemplates import (
    CONTAINER_ARRIVAL_CFP_TEMPLATE,
    ContainerArrivalCFPMsgBody,
    ContainerArrivalProposeMsgBody,
    ContainerArrivalRefuseMsgBody,
)
from messageTemplates.msgDecoder import decode_msg
from datetime import datetime, timedelta
from time import time, sleep


class CraneAgent(ThreadCachingAgent):
    def __init__(
        self,
        jid: str,
        password: str,
        location: str,
        docks_ids: list[int],
        transfer_points_ids: list[int],
        yellow_pages_jid: str,
    ):
        super().__init__(jid, password)
        self.location = location
        self.docks_ids = docks_ids
        self.transfer_points_ids = transfer_points_ids
        self.yellow_pages_jid = yellow_pages_jid
        self.container_arrival_threads_body = {}
        self.container_arrival_threads_reply_by = {}

    async def setup(self):
        await super().setup()
        self.add_behaviour(
            self.RegisterBehav(),
            template=(REGISTER_AGREE_TEMPLATE | REGISTER_REFUSE_TEMPLATE),
        )
        self.log("Crane agent started")

    async def get_transtainers_list(self, parent_behaviour) -> list[str]:
        log = self.log

        transtainers_list_request = TranstainerListRequestMsgBody(self.location)
        await parent_behaviour.send(
            transtainers_list_request.create_message(self.yellow_pages_jid)
        )

        transtainers_list = await parent_behaviour.receive(timeout=30)
        if transtainers_list is None:
            log("No transtainers available.")
            return None

        transtainers_list = decode_msg(transtainers_list).service_jids
        return transtainers_list

    class RegisterBehav(OneShotBehaviour):
        async def run(self):
            log = self.agent.log
            body = CraneRegistrationMsgBody(
                str(self.agent.jid),
                self.agent.location,
                self.agent.docks_ids,
                self.agent.transfer_points_ids,
            )

            await self.send(body.create_message(self.agent.yellow_pages_jid))
            log(
                f"Register request sent to yellow pages agent [{self.agent.yellow_pages_jid}]"
            )

            start_time = time()
            while time() - start_time < 30:
                reply = await self.receive(timeout=30)
                if not reply or str(reply.sender) != self.agent.yellow_pages_jid:
                    continue

                if REGISTER_AGREE_TEMPLATE.match(reply):
                    log("Registration accepted")
                    return

                elif REGISTER_REFUSE_TEMPLATE.match(reply):
                    log("Registration refused")

                else:
                    log("Unexpected reply")

            log("Failed to register. Shutting down...")
            self.kill()

        async def on_end(self):
            self.agent.add_behaviour(
                self.agent.ContainerArrivalCFPBehav(),
                template=(
                    CONTAINER_ARRIVAL_CFP_TEMPLATE | SERVICES_LIST_INFORM_TEMPLATE
                ),
            )

    class ContainerArrivalCFPBehav(CyclicBehaviour):
        async def run(self):
            log = self.agent.log
            msg = await self.receive(timeout=30)
            if not msg:
                return

            log(f"Received container arrival CFP from [{msg.sender}]")
            body = decode_msg(msg)
            if not body:
                log("Invalid message")
                return

            msg_reply_by = datetime.fromisoformat(msg.get_metadata("reply-by"))
            if msg_reply_by < datetime.now() + timedelta(seconds=10):
                log("Not enough time to process")
                return

            transtainer_list = await self.agent.get_transtainers_list(self)
            if not transtainer_list:
                self.send(
                    ContainerArrivalRefuseMsgBody().create_message(
                        str(msg.sender), msg.thread
                    )
                )
                return

            self.agent.container_arrival_threads_body[msg.thread] = body
            self.agent.container_arrival_threads_reply_by[msg.thread] = msg_reply_by

            transtainer_cfp = ContainerArrivalCFPMsgBody(body.container_ids, body.date)
            for transtainer in transtainer_list:
                await self.send(
                    transtainer_cfp.create_message(
                        transtainer, msg_reply_by - timedelta(seconds=10), msg.thread
                    )
                )
