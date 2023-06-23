from operator import contains
from typing import List
from agents.loggingAgent import LoggingAgent
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
)
from time import time

CONTAINER_REQUEST = Template()
CONTAINER_REQUEST.set_metadata("internal", "container_request")
CRANE_PROPOSAL = Template()
CRANE_PROPOSAL.set_metadata("internal", "crane_offer")
STAINER_OFFER_REQUEST = Template()
STAINER_OFFER_REQUEST.set_metadata("internal", "stainer_offer")


class TranstainerAgent(LoggingAgent):
    def __init__(
        self,
        jid: str,
        password: str,
        location: str,
        transfer_point_id: int,
        yellow_pages_jid: str,
    ):
        super().__init__(jid, password)
        self.yellow_pages_jid = yellow_pages_jid
        self.containers: List[str] = []
        self.location = location
        self.transfer_point_id = transfer_point_id

    async def setup(self):
        self.add_behaviour(
            self.RegisterBehav(),
            template=(REGISTER_AGREE_TEMPLATE | REGISTER_REFUSE_TEMPLATE),
        )
        self.log("Transtainer agent started")

    def set_containers(self, cnt):
        self.containers = cnt

    class RegisterBehav(OneShotBehaviour):
        async def run(self):
            log = self.agent.log
            body = TranstainerRegistrationMsgBody(
                str(self.agent.jid),
                self.agent.location,
                self.agent.transfer_point_id,
            )

            await self.send(body.create_message(to=self.agent.yellow_pages_jid))
            log(f"Register request sent to yellow pages agent [{self.agent.yellow_pages_jid}]")

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
            self.agent.add_behaviour(self.agent.RecvBehav())

    class RecvBehav(CyclicBehaviour):
        async def run(self):
            log = self.agent.log

            msg = await self.receive(timeout=100)
            # if msg:
            #     log(
            #         "Message received with content: {} from: {}".format(
            #             msg.body, msg.sender
            #         )
            #     )
            #     if CONTAINER_REQUEST.match(msg):
            #         # Got message from Port agent with request for some container
            #         if msg.body.split(",")[0] in self.agent.containers:
            #             # If the transtainer contains the container
            #             crane_req = Message(to=self.agent.crane_jid)
            #             crane_req.set_metadata("internal", "crane_price_request")
            #             crane_req.set_metadata(
            #                 "client_jid", msg.get_metadata("client_jid")
            #             )
            #             crane_req.body = msg.body.split(",")[1]
            #             await self.send(crane_req)
            #         else:
            #             log("Container not here")
            #             response = Message(to=str(msg.sender))
            #             response.set_metadata("internal", "negative")
            #             response.set_metadata(
            #                 "client_jid", msg.get_metadata("client_jid")
            #             )
            #             response.body = "No"
            #             await self.send(response)

            #     elif CRANE_PROPOSAL.match(msg):
            #         # Got crane offer for solving the container
            #         if msg.body != "No":
            #             price = msg.body
            #             response = Message(to=port_jid)
            #             response.set_metadata("internal", "positive")
            #             response.set_metadata(
            #                 "client_jid", str(msg.get_metadata("client_jid"))
            #             )
            #             response.body = str(price)
            #             await self.send(response)
            #         else:
            #             response = Message(to=str(msg.sender))
            #             response.set_metadata("internal", "negative")
            #             response.set_metadata(
            #                 "client_jid", str(msg.get_metadata("client_jid"))
            #             )
            #             response.body = "No"
            #             await self.send(response)

            #     elif STAINER_OFFER_REQUEST.match(msg):
            #         # TODO: Set up capacity with some mapping
            #         response = Message(to=str(msg.sender))
            #         response.set_metadata("internal", "stainer_offer_resp")
            #         response.set_metadata(
            #             "client_jid", str(msg.get_metadata("client_jid"))
            #         )

            #         # TODO: Implement logic here
            #         if random.randint(0, 1) == 1:
            #             response.set_metadata("result", "accept")
            #             response.body = random.randint(20, 100)
            #         else:
            #             response.set_metadata("result", "reject")
            #             response.body = "No"

            #         await self.send(response)

            # else:
            #     log(
            #         "Did not received any message after: {} seconds".format(
            #             message_wait_timeout
            #         )
            #     )
