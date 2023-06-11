from agents.loggingAgent import LoggingAgent
from spade.message import Message
from spade.behaviour import FSMBehaviour, State, PeriodicBehaviour, OneShotBehaviour, CyclicBehaviour
from spade.template import Template

CLIENT_PICKUP_REQUEST = Template()
CLIENT_PICKUP_REQUEST.set_metadata("propose", "pickup_proposal")

CLIENT_DROP_REQUEST = Template()
CLIENT_DROP_REQUEST.set_metadata("propose", "drop_proposal")

JOIN_REQUEST = Template()
JOIN_REQUEST.set_metadata("join", "join_request")

class PortAgent(LoggingAgent):
    class RecvBehav(CyclicBehaviour):
        async def run(self):
            log = self.agent.log
            message_wait_timeout = 100
            msg = await self.receive(timeout=message_wait_timeout)

            if msg:
                if JOIN_REQUEST.match(msg):
                    if msg.body == "transtainer":
                        self.agent.transtainers.append(str(msg.sender))
                        log(f"Transtainer [{str(msg.sender)}] joined")
                    elif msg.body == "crane":
                        self.agent.cranes.append(str(msg.sender))
                        log(f"Crane [{str(msg.sender)}] joined")

                elif CLIENT_PICKUP_REQUEST.match(msg):
                    #message from client
                    for stainer in self.agent.transtainers:
                        snd = Message(to=stainer)
                        snd.set_metadata("internal", "container_request")
                        snd.set_metadata("client_jid", str(msg.sender))
                        snd.body = msg.body
                        await self.send(snd)
                        log(f"Request sent to transtainer [{stainer}]!")

                elif CLIENT_DROP_REQUEST.match(msg):
                    containerIDs = msg.body[:msg.body.index(';')].split(',')
                    arrivalDate = msg.body[msg.body.index(';')+1:]
                    for crane in self.agent.cranes:
                        snd = Message(to=crane)
                        snd.set_metadata("internal", "crane_dropoff_request")
                        snd.set_metadata("client_jid", str(msg.sender))
                        snd.set_metadata("arrival_date", arrivalDate)
                        snd.body = f"{containerIDs.count}"
                        await self.send(snd)
                        log(f"Request sent to crane [{crane}]!")
                        
                elif str(msg.sender) in self.agent.transtainers:
                    # Message from transtainer
                    if(msg.body != "No"):
                        ans = Message(to=msg.get_metadata("client_jid"))
                        ans.set_metadata("internal", "container_request")
                        ans.body = "YES"
                        await self.send(ans)
                        log(f"Answer sent to client [{str(ans.to)}]!")
                else:
                    pass
  
            else:
                log("Did not received any message after: {} seconds".format(message_wait_timeout))


        async def on_end(self):
            log = self.agent.log
            log("Port Agent listening ...")

    async def setup(self):
        log = self.log
        log("Main Port agent started")
        self.transtainers = []
        self.cranes = []
        b = self.RecvBehav()
        self.add_behaviour(b)
        