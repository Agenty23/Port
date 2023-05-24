from operator import contains
from typing import List
from spade.agent import Agent
from spade.message import Message
from spade.behaviour import FSMBehaviour, State, PeriodicBehaviour, OneShotBehaviour, CyclicBehaviour
import datetime
from spade.template import Template

CONTAINER_REQUEST = Template()
CONTAINER_REQUEST.set_metadata("internal", "container_request")
CRANE_PROPOSAL = Template()
CRANE_PROPOSAL.set_metadata("internal","crane_offer")

def log(name, message):
    print("[",datetime.datetime.now(),"] ",name," ",message)


class TranstainerAgent(Agent):
    def __init__(self, jid, password, port_jid, crane_jid):
        super().__init__(jid, password)
        self.port_jid = str(port_jid)
        self.crane_jid = str(crane_jid)

    class JoinPortBehav(OneShotBehaviour):
        async def run(self):
            msg = Message(to=self.agent.port_jid)
            msg.set_metadata("join", "join_request")
            msg.body = "transtainer"
            await self.send(msg)
            print("Join request sent to port agent")
        
        async def on_end(self):
            self.agent.add_behaviour(self.agent.RecvBehav())
    
    class RecvBehav(CyclicBehaviour):
        async def run(self):
            message_wait_timeout = 100
            port_jid = self.agent.port_jid

            msg = await self.receive(timeout=100)
            if msg:
                log(self.agent.agent_name,"Message received with content: {} from: {}".format(msg.body,msg.sender))
                if CONTAINER_REQUEST.match(msg):
                    # Got message from Port agent with request for some container
                    if msg.body.split(',')[0] in self.agent.containers:
                        # If the transtainer contains the container
                        crane_req = Message(to=self.agent.crane_jid)
                        crane_req.set_metadata("internal", "crane_price_request")
                        crane_req.set_metadata("client_jid", msg.get_metadata("client_jid"))
                        crane_req.body = msg.body.split(',')[1]
                        await self.send(crane_req)
                    else:
                        log(self.agent.agent_name,"Container not here")
                        response = Message(to=str(msg.sender))
                        response.set_metadata("internal", "negative")
                        response.set_metadata("client_jid", msg.get_metadata("client_jid"))
                        response.body = "No"
                        await self.send(response)
                elif CRANE_PROPOSAL.match(msg):
                    # Got crane offer for solving the container
                    if msg.body != "No":
                        price = msg.body
                        response = Message(to=port_jid)
                        response.set_metadata("internal", "positive")
                        response.set_metadata("client_jid", str(msg.get_metadata("client_jid")))
                        response.body = str(price)
                        await self.send(response)
                    else:
                        response = Message(to=str(msg.sender))
                        response.set_metadata("internal", "negative")
                        response.set_metadata("client_jid", str(msg.get_metadata("client_jid")))
                        response.body = "No"
                        await self.send(response)
            else:
                print("Did not received any message after: {} seconds".format(message_wait_timeout))

    
    async def setup(self):
        print("Transtainer agent started")
        self.containers : List[str] = []
        b = self.JoinPortBehav()
        self.add_behaviour(b)
    
    def set_name(self,name):
        self.agent_name = name

    def set_containers(self,cnt):
        self.containers = cnt
    