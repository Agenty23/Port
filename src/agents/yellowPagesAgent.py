from agents.loggingAgent import LoggingAgent
from spade.message import Message
from spade.behaviour import CyclicBehaviour
from messageTemplates.msgBody import MsgBody
from messageTemplates.yellowPagesAgentTemplates import (
    portRegistration,
    craneRegistration,
    transtainerRegistration,
    portListRequest,
    craneListRequest,
    transtainerListRequest,
    REGISTER_REQUEST,
    SERVICES_LIST_QUERY_REF,
)


class YellowPagesAgent(LoggingAgent):
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.port_registrations = []
        self.crane_registrations = []
        self.transtainer_registrations = []

    class RegisterBehav(CyclicBehaviour):
        async def run(self):
            log = self.agent.log
            message_wait_timeout = 100
            log("Waiting for registration message...")

            msg = await self.receive(timeout=message_wait_timeout)
            if not msg:
                log(
                    f"Did not received any message after {message_wait_timeout} seconds."
                )
                return

            reply = Message(to=msg.sender)
            reply.set_metadata("performative", "agree")

            body = MsgBody.from_json(msg.body)
            if not body:
                reply.set_metadata("performative", "not-understood")

            elif type(body) is portRegistration:
                self.agent.port_registrations.append(body)

            elif type(body) is craneRegistration:
                self.agent.crane_registrations.append(body)

            elif type(body) is transtainerRegistration:
                self.agent.transtainer_registrations.append(body)

            else:
                log("Received message with unknown body type")
                reply.set_metadata("performative", "not-understood")

            await self.send(reply)

    class ServiceListBehav(CyclicBehaviour):
        async def run(self):
            log = self.agent.log
            message_wait_timeout = 100
            log("Waiting for service list request...")

            msg = await self.receive(timeout=message_wait_timeout)
            if not msg:
                log(
                    f"Did not received any message after {message_wait_timeout} seconds."
                )
                return

            reply = Message(to=msg.sender)
            reply.set_metadata("performative", "inform")

            body = msg.body
            if not body:
                log("Received message without body")
                reply.set_metadata("performative", "not-understood")

            elif type(body) is portListRequest:
                ports = [
                    x.portJid
                    for x in self.agent.port_registrations
                    if body.location == x.location
                ]
                reply.body = MsgBody.to_json(ports)

            elif type(body) is craneListRequest:
                cranes = [
                    x.craneJid
                    for x in self.agent.crane_registrations
                    if body.location == x.location and body.dockId in x.dockIds
                ]
                reply.body = MsgBody.to_json(cranes)

            elif type(body) is transtainerListRequest:
                transtainers = [
                    x.transtainerJid
                    for x in self.agent.transtainer_registrations
                    if body.location == x.location
                    and body.transferPointId == x.transferPointId
                ]
                reply.body = MsgBody.to_json(transtainers)

            else:
                log("Received message with unknown body")
                reply.set_metadata("performative", "not-understood")

            await self.send(reply)


    async def setup(self):
        self.log("YellowPagesAgent starting...")
        self.add_behaviour(self.RegisterBehav(), template=REGISTER_REQUEST)
        self.add_behaviour(self.ServiceListBehav(), template=SERVICES_LIST_QUERY_REF)
        self.log("YellowPagesAgent started")
