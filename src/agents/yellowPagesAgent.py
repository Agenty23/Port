from agents.loggingAgent import LoggingAgent
from spade.message import Message
from spade.behaviour import CyclicBehaviour
from messageTemplates.msgDecoder import decode_msg
from messageTemplates.yellowPagesAgentTemplates import (
    PortRegistrationMsgBody,
    CraneRegistrationMsgBody,
    TranstainerRegistrationMsgBody,
    RegistrationAgreeResponseMsgBody,
    ServicesListResponseMsgBody,
    PortListRequestMsgBody,
    CraneListRequestMsgBody,
    TranstainerListRequestMsgBody,
    REGISTER_REQUEST_TEMPLATE,
    SERVICES_LIST_QUERY_REF_TEMPLATE,
)
from messageTemplates.basicTemplates import NotUnderstoodMsgBody


class YellowPagesAgent(LoggingAgent):
    def __init__(self, jid: str, password: str):
        super().__init__(jid, password)
        self.port_registrations = []
        self.crane_registrations = []
        self.transtainer_registrations = []

    async def setup(self):
        self.add_behaviour(self.RegisterBehav(), template=REGISTER_REQUEST_TEMPLATE)
        self.add_behaviour(
            self.ServiceListBehav(), template=SERVICES_LIST_QUERY_REF_TEMPLATE
        )
        self.log("YellowPagesAgent started")

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

            body = decode_msg(msg)

            if not body:
                log("Got message with no body!")
                replyBody = NotUnderstoodMsgBody()

            else:
                replyBody = RegistrationAgreeResponseMsgBody()
                if type(body) is PortRegistrationMsgBody:
                    log(f"Port [{body.port_jid}] registered!")
                    self.agent.port_registrations.append(body)

                elif type(body) is CraneRegistrationMsgBody:
                    log(f"Crane [{body.crane_jid}] registered!")
                    self.agent.crane_registrations.append(body)

                elif type(body) is TranstainerRegistrationMsgBody:
                    log(f"Transtainer [{body.transtainer_jid}] registered!")
                    self.agent.transtainer_registrations.append(body)

                else:
                    log("Got message with unknown body!")
                    replyBody = NotUnderstoodMsgBody()

            await self.send(replyBody.create_message(str(msg.sender)))

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

            body = decode_msg(msg)
            if not body:
                log("Received message without body")
                replyBody = NotUnderstoodMsgBody()

            else:
                if type(body) is PortListRequestMsgBody:
                    servicesList = [
                        x.port_jid
                        for x in self.agent.port_registrations
                        if body.location == x.location
                    ]
                    replyBody = ServicesListResponseMsgBody(servicesList)

                elif type(body) is CraneListRequestMsgBody:
                    servicesList = [
                        x.crane_jid
                        for x in self.agent.crane_registrations
                        if body.location == x.location and body.dockId in x.dockIds
                    ]
                    replyBody = ServicesListResponseMsgBody(servicesList)

                elif type(body) is TranstainerListRequestMsgBody:
                    servicesList = [
                        x.transtainer_jid
                        for x in self.agent.transtainer_registrations
                        if body.location == x.location
                        and body.transfer_point_id == x.transfer_point_id
                    ]
                    replyBody = ServicesListResponseMsgBody(servicesList)

                else:
                    log("Received message with unknown body")
                    replyBody = NotUnderstoodMsgBody()

            await self.send(replyBody.create_message(str(msg.sender)))
