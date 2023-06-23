import random
from typing import List
from agents.loggingAgent import LoggingAgent
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
)
import datetime
from time import time, sleep

PICKUP_PROPOSAL = Template()
PICKUP_PROPOSAL.set_metadata("internal", "crane_price_request")

DROPOFF_PROPOSAL = Template()
DROPOFF_PROPOSAL.set_metadata("internal", "crane_dropoff_request")

STAINER_OFFER_PROPOSAL = Template()
STAINER_OFFER_PROPOSAL.set_metadata("internal", "stainer_offer_resp")

TRANSTAINER_JOIN_REQUEST = Template()
TRANSTAINER_JOIN_REQUEST.set_metadata("join", "crane_join_request")


class CraneAgent(LoggingAgent):
    def __init__(
        self,
        jid: str,
        password: str,
        location: str,
        docks_ids: list[int],
        transfer_points_ids: list[int],
        yellow_pages_jids: list[str],
    ):
        super().__init__(jid, password)
        self.location = location
        self.docks_ids = docks_ids
        self.transfer_points_ids = transfer_points_ids
        self.yellow_pages_jids = yellow_pages_jids

    async def setup(self):
        self.add_behaviour(
            self.RegisterBehav(),
            template=(REGISTER_AGREE_TEMPLATE | REGISTER_REFUSE_TEMPLATE),
        )
        self.log("Crane agent started")

    class RegisterBehav(OneShotBehaviour):
        async def run(self):
            log = self.agent.log
            body = CraneRegistrationMsgBody(
                str(self.agent.jid),
                self.agent.location,
                self.agent.docks_ids,
                self.agent.transfer_points_ids,
            )

            for yellow_pages_jid in self.agent.yellow_pages_jids:
                await self.send(body.create_message(yellow_pages_jid))
                log(f"Register request sent to yellow pages agent [{yellow_pages_jid}]")

                start_time = time()
                while time() - start_time < 30:
                    reply = await self.receive(timeout=30)
                    if not reply or str(reply.sender) != yellow_pages_jid:
                        continue

                    if REGISTER_AGREE_TEMPLATE.match(reply):
                        log("Registration accepted")
                        return

                    elif REGISTER_REFUSE_TEMPLATE.match(reply):
                        log("Registration refused")

                    else:
                        log("Unexpected reply")

                log("Register request timeout")

            log("Not registered to any yellow pages agent. Shutting down...")
            self.kill()

        async def on_end(self):
            self.agent.add_behaviour(self.agent.RecvBehav())

    class RecvBehav(CyclicBehaviour):
        async def run(self):
            log = self.agent.log

            msg = await self.receive(timeout=100)
            # if not msg:
            #     log(
            #         "Did not received any message after: {} seconds".format(
            #             message_wait_timeout
            #         )
            #     )
            #     return

            # if TRANSTAINER_JOIN_REQUEST.match(msg):
            #     self.agent.transtainers.append(str(msg.sender))
            #     log(f"Transtainer [{str(msg.sender)}] joined")

            # elif PICKUP_PROPOSAL.match(msg):
            #     log("Message received with content: {}".format(msg.body))
            #     res = Message(to=str(msg.sender))
            #     res.set_metadata("internal", "crane_offer")
            #     res.set_metadata("client_jid", msg.get_metadata("client_jid"))
            #     res.body = str(random.randint(20, 100))
            #     await self.send(res)

            # elif DROPOFF_PROPOSAL.match(msg):
            #     log("Message received with content: {}".format(msg.body))
            #     for stainers in self.agent.transtainers:
            #         snd = Message(to=stainers)
            #         snd.set_metadata("internal", "stainer_offer")
            #         snd.set_metadata("client_jid", msg.get_metadata("client_jid"))
            #         snd.set_metadata("arrival_date", msg.get_metadata("arrival_date"))
            #         snd.body = msg.body
            #         await self.send(snd)
            #         log(f"Request sent to transtainer [{stainers}]!")

            # # elif STAINER_OFFER_PROPOSAL.match(msg):
            # #     if msg.get_metadata("result") == "accept":
