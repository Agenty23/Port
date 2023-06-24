from agents.threadCachingAgent import ThreadCachingAgent
from spade.message import Message
from spade.behaviour import OneShotBehaviour, CyclicBehaviour, PeriodicBehaviour
from messageTemplates.yellowPagesAgentTemplates import (
    PortRegistrationMsgBody,
    REGISTER_AGREE_TEMPLATE,
    REGISTER_REFUSE_TEMPLATE,
    CraneListRequestMsgBody,
    SERVICES_LIST_INFORM_TEMPLATE,
)
from messageTemplates.containerArrivalTemplates import (
    CONTAINER_ARRIVAL_CFP_TEMPLATE,
    ContainerArrivalCFPMsgBody,
    ContainerArrivalProposeMsgBody,
    ContainerArrivalRefuseMsgBody,
)
from messageTemplates.basicTemplates import BLOCK_TEMPLATE
from time import time, sleep
from messageTemplates.msgDecoder import decode_msg
from datetime import datetime, timedelta


class PortAgent(ThreadCachingAgent):
    def __init__(self, jid: str, password: str, location: str, yellow_pages_jid: str):
        super().__init__(jid, password)
        self.location = location
        self.yellow_pages_jid = yellow_pages_jid
        self.container_arrival_threads_body = {}
        self.container_arrival_threads_reply_by = {}

    async def setup(self):
        await super().setup()
        self.add_behaviour(
            self.RegisterBehav(),
            template=(REGISTER_AGREE_TEMPLATE | REGISTER_REFUSE_TEMPLATE),
        )
        self.log("PortAgent started")

    async def get_cranes_list(self, parent_behaviour) -> list[str]:
        log = self.log

        cranes_list_request = CraneListRequestMsgBody(self.location)
        await parent_behaviour.send(
            cranes_list_request.create_message(self.yellow_pages_jid)
        )

        cranes_list = await parent_behaviour.receive(timeout=30)
        if cranes_list is None:
            log("No cranes available.")
            return None

        cranes_list = decode_msg(cranes_list).service_jids
        return cranes_list

    class RegisterBehav(OneShotBehaviour):
        async def run(self):
            log = self.agent.log
            body = PortRegistrationMsgBody(str(self.agent.jid), self.agent.location)

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

            cranes_list = await self.agent.get_cranes_list(self)
            if not cranes_list:
                self.send(
                    ContainerArrivalRefuseMsgBody().create_message(
                        str(msg.sender), msg.thread
                    )
                )
                return

            self.agent.container_arrival_threads_body[msg.thread] = body
            self.agent.container_arrival_threads_reply_by[msg.thread] = msg_reply_by

            crane_cfp = ContainerArrivalCFPMsgBody(body.container_ids, body.date)
            for crane in cranes_list:
                await self.send(
                    crane_cfp.create_message(
                        crane, msg_reply_by - timedelta(seconds=10), msg.thread
                    )
                )
