from spade.agent import Agent
from spade.message import Message
from spade.behaviour import FSMBehaviour, State, PeriodicBehaviour, OneShotBehaviour
import datetime

class PortAgent(Agent):
    async def setup(self):
        print("Main Port agent started")
        