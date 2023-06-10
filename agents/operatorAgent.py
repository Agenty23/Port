from agents.loggingAgent import LoggingAgent
from spade.message import Message
from spade.behaviour import OneShotBehaviour
import datetime
from spade.message import Message
from spade.template import Template

class OperatorAgent(LoggingAgent):
    def __init__(self, jid, password, action, port_jid):
        super().__init__(jid, password)
        self.action = action
        self.port_jid = str(port_jid)

    class RequestContainerBehaviour(OneShotBehaviour):
        async def on_start(self):
            print("------------Input section-------------")
            print("How many containers do you want to get?")
            self.nContainers = int(input())
            self.containerID = []
            for _ in range(self.nContainers):
                print("Please enter container ID:")
                self.containerID.append(input())
            print("Please enter date of collection(dd-mm-yyyy)")
            self.collection = datetime.datetime.strptime(input(),'%d-%m-%Y').date()
            print("\n")

        async def run(self):
            log = self.agent.log
            log(f"Containers to get: {self.containerID}")
            log(f"Pick up date: {self.collection}")

            msg = Message(to=self.agent.port_jid)
            msg.set_metadata("propose", "pickup_proposal")
            msg.body = f"{self.containerID[0]},{self.collection.strftime('%d-%m-%Y')}"
            await self.send(msg)
            log(f"Request sent to port {self.agent.port_jid}")

            message_wait_timeout = 10
            msg = await self.receive(timeout=message_wait_timeout)
            if msg:
                log("Client received with content: {}".format(msg.body))
            else:
                log("Did not received any message after: {} seconds".format(message_wait_timeout))

            self.kill(exit_code=0)

    class RegisterContainerBehaviour(OneShotBehaviour):
        async def on_start(self):
            print("------------Input section-------------")
            print("Please enter container IDs (comma separated):")
            self.containerIDs = input().split(',')
            print("Please enter date of arrival(dd-mm-yyyy)")
            self.arrival = datetime.datetime.strptime(input(),'%d-%m-%Y').date()
            print("\n")

        async def run(self):
            log = self.agent.log
            log(f"Containers to store: {self.containerIDs}")
            log(f"Arrival date: {self.arrival}")
            
            msg = Message(to=self.agent.port_jid)
            msg.set_metadata("propose", "drop_proposal")
            msg.body = f"{self.containerIDs};{self.arrival.strftime('%d-%m-%Y')}"
            await self.send(msg)
            log(f"Request sent to port {self.agent.port_jid}")

            message_wait_timeout = 10
            msg = await self.receive(timeout=message_wait_timeout)
            if msg:
                log("Client received with content: {}".format(msg.body))
            else:
                log("Did not received any message after: {} seconds".format(message_wait_timeout))

            self.kill(exit_code=0)

    async def setup(self):
        log = self.log
        log("Operator agent started")
        if self.action == "pickup":
            b = self.RequestContainerBehaviour()
        elif self.action == "dropoff":
            b = self.RegisterContainerBehaviour()
        else:
            raise ValueError("Unknown action")
        self.add_behaviour(b)
