from operator import contains
from typing import List

from spade.container import Container
from agents.threadCachingAgent import ThreadCachingAgent
from spade.message import Message
from spade.behaviour import (
    FSMBehaviour,
    State,
    PeriodicBehaviour,
    OneShotBehaviour,
    CyclicBehaviour,
)
import random
from spade.template import Template
from messageTemplates.yellowPagesAgentTemplates import (
    TranstainerRegistrationMsgBody,
    REGISTER_AGREE_TEMPLATE,
    REGISTER_REFUSE_TEMPLATE,
    SERVICES_LIST_INFORM_TEMPLATE,
)
from time import time
from messageTemplates.msgDecoder import decode_msg
from datetime import datetime, timedelta
from messageTemplates.containerArrivalTemplates import (
    CONTAINER_ARRIVAL_CFP_TEMPLATE,
    ContainerArrivalCFPMsgBody,
    ContainerArrivalProposeMsgBody,
    ContainerArrivalRefuseMsgBody,
)
import numpy as np


class TranstainerAgent(ThreadCachingAgent):
    def __init__(
        self,
        jid: str,
        password: str,
        location: str,
        transfer_point_id: int,
        yellow_pages_jid: str,
        yard: np.ndarray = np.empty((5, 5, 5), dtype=str)
    ):
        super().__init__(jid, password)
        self.yellow_pages_jid = yellow_pages_jid
        self.containers: List[str] = []
        self.location = location
        self.transfer_point_id = transfer_point_id
        self.yard = yard

    async def setup(self):
        await super().setup()
        self.add_behaviour(
            self.RegisterBehav(),
            template=(REGISTER_AGREE_TEMPLATE | REGISTER_REFUSE_TEMPLATE),
        )
        self.log("Transtainer agent started")

    class RegisterBehav(OneShotBehaviour):
        async def run(self):
            log = self.agent.log
            body = TranstainerRegistrationMsgBody(
                str(self.agent.jid),
                self.agent.location,
                self.agent.transfer_point_id,
            )

            await self.send(body.create_message(to=self.agent.yellow_pages_jid))
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

            local_containers = []
            for container in body.container_ids:
                if container in self.agent.containers:
                    local_containers.append(container)
