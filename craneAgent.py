import random
from typing import List
from spade.agent import Agent
from spade.message import Message
from spade.behaviour import FSMBehaviour, State, PeriodicBehaviour, CyclicBehaviour, OneShotBehaviour
import datetime

def log(name, message):
    print("[",datetime.datetime.now(),"] ",name," ",message)

class CraneAgent(Agent):
    def __init__(self, jid, password, port_jid):
        super().__init__(jid, password)
        self.port_jid = str(port_jid)

    class JoinPortBehav(OneShotBehaviour):
        async def run(self):
            msg = Message(to=self.agent.port_jid)
            msg.set_metadata("join", "join_request")
            msg.body = "crane"
            await self.send(msg)
            print("Join request sent to port agent")
        
        async def on_end(self):
            self.agent.add_behaviour(self.agent.RecvBehav())

    class RecvBehav(CyclicBehaviour):
        async def run(self):
            message_wait_timeout = 100

            msg = await self.receive(timeout=100)
            if msg:
                log(self.agent.agent_name,"Message received with content: {}".format(msg.body))
                res = Message(to=str(msg.sender))
                res.set_metadata("internal","crane_offer")
                res.body = str(random.randint(20,100))
                await self.send(res)

            else:
                print("Did not received any message after: {} seconds".format(message_wait_timeout))

    async def setup(self):
        print("Crane agent started")
        b = self.JoinPortBehav()
        self.add_behaviour(b)
    
    def set_name(self,name):
        self.agent_name = name
        