from operator import contains
from typing import List
from spade.agent import Agent
from spade.message import Message
from spade.behaviour import FSMBehaviour, State, PeriodicBehaviour, OneShotBehaviour, CyclicBehaviour
import datetime

def log(name, message):
    print("[",datetime.datetime.now(),"] ",name," ",message)


class TranstainerAgent(Agent):
    
    class RecvBehav(CyclicBehaviour):
        async def run(self):
            message_wait_timeout = 100

            msg = await self.receive(timeout=100)
            if msg:
                log(self.agent.agent_name,"Message received with content: {}".format(msg.body))
                if msg.body.split(',')[0] in self.agent.containers:
                    print("Container here")
                    crane_req = Message(to="test_agent@jabbim.pl/9")
                    crane_req.set_metadata("internal", "crane_price_request")
                    crane_req.body = msg.body.split(',')[1]
                    await self.send(crane_req)
                    msg2 = await self.receive(timeout=100)
                    if msg2:
                        if msg2.body != "No":
                            price = msg2.body
                            response = Message(to=str(msg.sender))
                            response.set_metadata("internal", "positive")
                            response.body = str(price)
                            await self.send(response)
                        else:
                            pass
                            # response = Message(to=str(msg.sender))
                            # response.set_metadata("internal", "negative")
                            # response.body = "No"
                            # await self.send(response)
                else:
                    print("Container not here")
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
    