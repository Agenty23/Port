from spade.agent import Agent
from spade.message import Message
from spade.behaviour import FSMBehaviour, State, PeriodicBehaviour, OneShotBehaviour, CyclicBehaviour
import datetime
from spade.template import Template

CLIENT_REQUEST = Template()
CLIENT_REQUEST.set_metadata("propose", "get_proposal")

JOIN_REQUEST = Template()
JOIN_REQUEST.set_metadata("join", "join_request")

def log(name, message):
    print("[",datetime.datetime.now(),"] ",name," ",message)

class PortAgent(Agent):
    class RecvBehav(CyclicBehaviour):
        async def run(self):
            message_wait_timeout = 10
            msg = await self.receive(timeout=message_wait_timeout)

            if msg:
                log(self.agent.agent_name,"Message received with content: {}".format(msg.body))

                if JOIN_REQUEST.match(msg):
                    if msg.body == "transtainer":
                        self.agent.transtainers.append(str(msg.sender))
                        log(self.agent.agent_name,f"Transtainer joined {str(msg.sender)}")
                    elif msg.body == "crane":
                        self.agent.cranes.append(str(msg.sender))
                        log(self.agent.agent_name,"Crane joined")

                elif CLIENT_REQUEST.match(msg):
                    #message from client
                    for stainer in self.agent.transtainers:
                        snd = Message(to=stainer)
                        snd.set_metadata("internal", "container_request")
                        snd.set_metadata("client_jid", str(msg.sender))
                        snd.body = msg.body
                        await self.send(snd)
                        log(self.agent.agent_name,f"Request sent to transtainer [{stainer}]!")

                elif str(msg.sender) in self.agent.transtainers:
                    # Message from transtainer
                    if(msg.body != "No"):
                        ans = Message(to=msg.get_metadata("client_jid"))
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
        self.transtainers = []
        self.cranes = []
        b = self.RecvBehav()
        self.add_behaviour(b)

    def set_name(self,name):
        self.agent_name = name
        