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
    
    class RecvBehav(CyclicBehaviour):
        async def run(self):
            message_wait_timeout = 100

            msg = await self.receive(timeout=100)
            if msg:
                log(self.agent.agent_name,"Message received with content: {} from: {}".format(msg.body,msg.sender))
                if str(msg.sender) == "port@jabbim.pl":#msg.match(CONTAINER_REQUEST):
                    # Got message from Port agent with request for some container
                    if msg.body.split(',')[0] in self.agent.containers:
                        # If the transtainer contains the container
                        crane_req = Message(to="test_agent@jabbim.pl/6")
                        crane_req.set_metadata("internal", "crane_price_request")
                        crane_req.body = msg.body.split(',')[1]
                        await self.send(crane_req)
                    else:
                        log(self.agent.agent_name,"Container not here")
                        response = Message(to=str(msg.sender))
                        response.set_metadata("internal", "negative")
                        response.body = "No"
                        await self.send(response)
                elif str(msg.sender) == "test_agent@jabbim.pl/6":#msg.match(CRANE_PROPOSAL):
                    # Got crane offer for solving the container
                    if msg.body != "No":
                        price = msg.body
                        response = Message(to="port@jabbim.pl")
                        response.set_metadata("internal", "positive")
                        response.body = str(price)
                        await self.send(response)
                    else:
                        response = Message(to=str(msg.sender))
                        response.set_metadata("internal", "negative")
                        response.body = "No"
                        await self.send(response)
            else:
                print("Did not received any message after: {} seconds".format(message_wait_timeout))

    
    async def setup(self):
        print("Transtainer agent started")
        self.containers : List[str] = []
        b = self.RecvBehav()
        self.add_behaviour(b)
    
    def set_name(self,name):
        self.agent_name = name

    def set_containers(self,cnt):
        self.containers = cnt
    