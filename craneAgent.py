from typing import List
from spade.agent import Agent
from spade.message import Message
from spade.behaviour import FSMBehaviour, State, PeriodicBehaviour, OneShotBehaviour
import datetime

class CraneAgent(Agent):
    continers : List[str] = []
    async def setup(self):
        print("Crane agent started")
        