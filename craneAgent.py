import random
from typing import List
from loggingAgent import LoggingAgent
from spade.message import Message
from spade.template import Template
from spade.behaviour import FSMBehaviour, State, PeriodicBehaviour, CyclicBehaviour, OneShotBehaviour
import datetime

PICKUP_PROPOSAL = Template()
PICKUP_PROPOSAL.set_metadata("internal", "crane_price_request")

DROPOFF_PROPOSAL = Template()
DROPOFF_PROPOSAL.set_metadata("internal", "crane_dropoff_request")

TRANSTAINER_JOIN_REQUEST = Template()
TRANSTAINER_JOIN_REQUEST.set_metadata("join", "crane_join_request")

class CraneAgent(LoggingAgent):

    def __init__(self, jid, password, port_jid):
        super().__init__(jid, password)
        self.port_jid = str(port_jid)

    class JoinPortBehav(OneShotBehaviour):
        async def run(self):
            log = self.agent.log
            msg = Message(to=self.agent.port_jid)
            msg.set_metadata("join", "join_request")
            msg.body = "crane"
            await self.send(msg)
            log("Join request sent to port agent")
        
        async def on_end(self):
            self.agent.add_behaviour(self.agent.RecvBehav())

    class RecvBehav(CyclicBehaviour):
        async def run(self):
            log = self.agent.log
            message_wait_timeout = 100

            msg = await self.receive(timeout=100)
            if not msg:
                log("Did not received any message after: {} seconds".format(message_wait_timeout))
                return

            if TRANSTAINER_JOIN_REQUEST.match(msg):
                self.agent.transtainers.append(str(msg.sender))
                log(f"Transtainer [{str(msg.sender)}] joined")
                
            elif PICKUP_PROPOSAL.match(msg):
                log("Message received with content: {}".format(msg.body))
                res = Message(to=str(msg.sender))
                res.set_metadata("internal","crane_offer")
                res.set_metadata("client_jid", msg.get_metadata("client_jid"))
                res.body = str(random.randint(20,100))
                await self.send(res)

            elif DROPOFF_PROPOSAL.match(msg):
                log("Message received with content: {}".format(msg.body))
                

    async def setup(self):
        log = self.log
        log("Crane agent started")
        b = self.JoinPortBehav()
        self.add_behaviour(b)
        self.transtainers = []
    
    def set_name(self,name):
        self.agent_name = name
        