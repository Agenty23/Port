from spade.agent import Agent
from spade.message import Message
from spade.behaviour import OneShotBehaviour
import datetime
from spade.message import Message
from spade.template import Template

class OperatorAgent(Agent):
    class RequestContainerBehaviour(OneShotBehaviour):
        async def on_start(self):
            print("How many containers do you want to get?")
            self.nContainers = int(input())
            self.containerID = []
            for _ in range(self.nContainers):
                print("Please enter container ID:")
                self.containerID.append(input())
            print("Please enter date of collection(dd-mm-yyyy)")
            self.collection = datetime.datetime.strptime(input(),'%d-%m-%Y').date()

        async def run(self):
            print("\nContainers:")
            for c in self.containerID:
                print(c)
            print("Collection: ",self.collection)
            print("\n")
            msg = Message(to="port@jabbim.pl")

            msg.set_metadata("propose", "get_proposal")
            msg.body = f"{self.containerID[0]},{self.collection.strftime('%d-%m-%Y')}"

            await self.send(msg)
            print("Request sent!")

            message_wait_timeout = 10

            msg = await self.receive(timeout=10)
            if msg:
                print("Client received with content: {}".format(msg.body))
            else:
                print("Did not received any message after: {} seconds".format(message_wait_timeout))

            self.kill(exit_code=0)

    async def setup(self):
        print("Operator agent started")
        b = self.RequestContainerBehaviour()
        self.add_behaviour(b)
