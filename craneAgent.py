import random
from typing import List
from spade.agent import Agent
from spade.message import Message
from spade.behaviour import FSMBehaviour, State, PeriodicBehaviour, CyclicBehaviour
import datetime

class CraneAgent(Agent):

    class RecvBehav(CyclicBehaviour):
        async def run(self):
            print("RecvBehav running")
            message_wait_timeout = 20

            msg = await self.receive(timeout=20)
            if msg:
                print(self.agent.__class__,"Message received with content: {}".format(msg.body))
                res = Message(to=msg.sender)
                res.set_metadata("internal","offer")
                res.body(random.randint(20,100))
                await self.send(res)

            else:
                print("Did not received any message after: {} seconds".format(message_wait_timeout))

    async def setup(self):
        print("Crane agent started")
        