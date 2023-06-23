from agents.loggingAgent import LoggingAgent
from spade.message import Message
from spade.behaviour import (
    FSMBehaviour,
    State,
    PeriodicBehaviour,
    OneShotBehaviour,
    CyclicBehaviour,
)
from spade.template import Template
from messageTemplates.basicTemplates import NotUnderstoodMsgBody
from messageTemplates.msgDecoder import decode_msg
from messageTemplates.yellowPagesAgentTemplates import (
    PortRegistrationMsgBody,
    REGISTER_AGREE_TEMPLATE,
    REGISTER_REFUSE_TEMPLATE,
)
from time import time, sleep

CLIENT_PICKUP_REQUEST = Template()
CLIENT_PICKUP_REQUEST.set_metadata("propose", "pickup_proposal")

CLIENT_DROP_REQUEST = Template()
CLIENT_DROP_REQUEST.set_metadata("propose", "drop_proposal")

JOIN_REQUEST = Template()
JOIN_REQUEST.set_metadata("join", "join_request")


class PortAgent(LoggingAgent):
    def __init__(
        self, jid: str, password: str, location: str, yellow_pages_jid: str
    ):
        super().__init__(jid, password)
        self.location = location
        self.yellow_pages_jid = yellow_pages_jid
        self.transtainers = []
        self.cranes = []

    async def setup(self):
        self.add_behaviour(
            self.RegisterBehav(),
            template=(REGISTER_AGREE_TEMPLATE | REGISTER_REFUSE_TEMPLATE),
        )
        self.log("PortAgent started")

    class RegisterBehav(OneShotBehaviour):
        async def run(self):
            log = self.agent.log
            body = PortRegistrationMsgBody(str(self.agent.jid), self.agent.location)

            await self.send(body.create_message(self.agent.yellow_pages_jid))
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
            #     if JOIN_REQUEST.match(msg):
            #         if msg.body == "transtainer":
            #             self.agent.transtainers.append(str(msg.sender))
            #             log(f"Transtainer [{str(msg.sender)}] joined")
            #         elif msg.body == "crane":
            #             self.agent.cranes.append(str(msg.sender))
            #             log(f"Crane [{str(msg.sender)}] joined")

            #     elif CLIENT_PICKUP_REQUEST.match(msg):
            #         # message from client
            #         for stainer in self.agent.transtainers:
            #             snd = Message(to=stainer)
            #             snd.set_metadata("internal", "container_request")
            #             snd.set_metadata("client_jid", str(msg.sender))
            #             snd.body = msg.body
            #             await self.send(snd)
            #             log(f"Request sent to transtainer [{stainer}]!")

            #     elif CLIENT_DROP_REQUEST.match(msg):
            #         container_ids = msg.body[: msg.body.index(";")].split(",")
            #         arrivalDate = msg.body[msg.body.index(";") + 1 :]
            #         for crane in self.agent.cranes:
            #             snd = Message(to=crane)
            #             snd.set_metadata("internal", "crane_dropoff_request")
            #             snd.set_metadata("client_jid", str(msg.sender))
            #             snd.set_metadata("arrival_date", arrivalDate)
            #             snd.body = f"{container_ids.count}"
            #             await self.send(snd)
            #             log(f"Request sent to crane [{crane}]!")

            #     elif str(msg.sender) in self.agent.transtainers:
            #         # Message from transtainer
            #         if msg.body != "No":
            #             ans = Message(to=msg.get_metadata("client_jid"))
            #             ans.set_metadata("internal", "container_request")
            #             ans.body = "YES"
            #             await self.send(ans)
            #             log(f"Answer sent to client [{str(ans.to)}]!")
            #     else:
            #         pass

            # else:
            #     log(
            #         f"Did not received any message after: {message_wait_timeout} seconds"
            #     )
