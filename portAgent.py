from spade.agent import Agent
from spade.message import Message
from spade.behaviour import FSMBehaviour, State, PeriodicBehaviour, OneShotBehaviour, CyclicBehaviour
import datetime
from spade.template import Template

CLIENT_REQUEST = Template()
CLIENT_REQUEST.set_metadata("propose", "get_proposal")

def log(name, message):
    print("[",datetime.datetime.now(),"] ",name," ",message)

class PortAgent(Agent):

    class RecvBehav(CyclicBehaviour):
        async def run(self):
            message_wait_timeout = 10

            msg = await self.receive(timeout=10)
            if msg:
                log(self.agent.agent_name,"Message received with content: {}".format(msg.body))
                if str(msg.sender) == "test_agent@jabbim.pl/2": #msg.match(CLIENT_REQUEST):
                    #message from client
                    for stainer in self.agent.transtainers:
                        snd = Message(to=stainer)
                        snd.set_metadata("internal", "container_request")
                        snd.body = msg.body
                        await self.send(snd)
                        log(self.agent.agent_name,"Request sent to transtainer!")
                elif str(msg.sender) in {"test_agent@jabbim.pl/3","test_agent@jabbim.pl/4","test_agent@jabbim.pl/5"}:
                    # Message from transtainer
                    if(msg.body != "No"):
                        ans = Message(to="test_agent@jabbim.pl/2")
                        ans.set_metadata("internal", "container_request")
                        ans.body = "YES"
                        await self.send(ans)
                        log(self.agent.agent_name,"Answer sent to client!")
                else:
                    pass
  
            else:
                print("Did not received any message after: {} seconds".format(message_wait_timeout))


        async def on_end(self):
            print("Port Agent listening ...")

    async def setup(self):
        print("Main Port agent started")
        self.transtainers = {"test_agent@jabbim.pl/3","test_agent@jabbim.pl/4","test_agent@jabbim.pl/5"}
        b = self.RecvBehav()
        self.add_behaviour(b)

    def set_name(self,name):
        self.agent_name = name
        