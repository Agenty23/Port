from spade.agent import Agent
from spade.message import Message
from spade.behaviour import FSMBehaviour, State, PeriodicBehaviour, OneShotBehaviour
import datetime
import time
import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour


class AskBehaviour(CyclicBehaviour):
        async def on_start(self):
            print("------------Starting-------------")

        async def run(self):
            msg = await self.receive(timeout=1000)
            message_sender : str = str(msg.sender)
            msg = Message(to=message_sender)
            msg.body = str(self.agent.weight)
            await self.send(msg)
            
class ContainerAgent(Agent):

    # portOfOrigin : str = None
    # weight : str = None

    

    
    async def setup(self):
        print("Container added to the system")
        b = self.AskBehaviour()
        self.add_behaviour(b)
        self.weight = 100
        self.port_of_origin = "Poland"



if __name__ == "__main__":
    dummy = ContainerAgent("test_agent@jabbim.pl", "123")
    dummy.start()
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break
    dummy.stop()