from agents.loggingAgent import LoggingAgent
from spade.behaviour import CyclicBehaviour
from messageTemplates.msgDecoder import decode_msg
from messageTemplates.agentRegistration import (
    REGISTER_REQUEST_TEMPLATE,
    RegistrationAgreeMsgBody,
    PortRegistrationRequestMsgBody,
    CraneRegistrationRequestMsgBody,
    TranstainerRegistrationRequestMsgBody,
)
from messageTemplates.servicesListRequest import (
    SERVICES_LIST_QUERY_REF_TEMPLATE,
    PortListQueryRefMsgBody,
    CraneListQueryRefMsgBody,
    TranstainerListQueryRefMsgBody,
    ServicesListInformMsgBody,
)


class YellowPagesAgent(LoggingAgent):
    # region Agent setup and registration
    def __init__(self, jid: str, password: str):
        """
        Creates a yellow pages agent instance.

        Args:
            jid (str): Yellow pages agent's JID.
            password (str): Yellow pages agent's password.
        """
        super().__init__(jid, password)
        self.port_registrations = []
        self.crane_registrations = []
        self.transtainer_registrations = []

    async def setup(self) -> None:
        self.add_behaviour(self.RegisterBehav(), template=REGISTER_REQUEST_TEMPLATE())
        self.add_behaviour(
            self.ServiceListBehav(), template=SERVICES_LIST_QUERY_REF_TEMPLATE()
        )
        self.log("YellowPagesAgent started")

    # endregion

    class RegisterBehav(CyclicBehaviour):
        def __init__(self):
            """Behaviour that listens for incoming agent's registration requests."""
            super().__init__()

        async def run(self) -> None:
            self.agent: YellowPagesAgent
            log = self.agent.log

            msg = await self.receive(timeout=100)
            if not msg:
                return

            body = decode_msg(msg)
            if not body:
                log("Got invalid message!")
                return

            if type(body) is PortRegistrationRequestMsgBody():
                log(f"Port [{body.port_jid}] registered!")
                self.agent.port_registrations.append(body)
            elif type(body) is CraneRegistrationRequestMsgBody:
                log(f"Crane [{body.crane_jid}] registered!")
                self.agent.crane_registrations.append(body)
            elif type(body) is TranstainerRegistrationRequestMsgBody:
                log(f"Transtainer [{body.transtainer_jid}] registered!")
                self.agent.transtainer_registrations.append(body)
            else:
                log("Got message with unknown body!")
                return

            await self.send(RegistrationAgreeMsgBody().create_message(str(msg.sender)))

    class ServiceListBehav(CyclicBehaviour):
        def __init__(self):
            """Behaviour that listens for incoming service list queries."""
            super().__init__()

        async def run(self) -> None:
            self.agent: YellowPagesAgent
            log = self.agent.log

            msg = await self.receive(timeout=100)
            if not msg:
                return

            body = decode_msg(msg)
            if not body:
                return

            if type(body) is PortListQueryRefMsgBody:
                log(f"Received port list request for location {body.location}")
                services = [
                    x
                    for x in self.agent.port_registrations
                    if body.location == x.location
                ]
            elif type(body) is CraneListQueryRefMsgBody:
                log(
                    f"Received crane list request for location {body.location}, docks {body.dock_ids} and transfer points {body.transfer_point_ids}"
                )
                services = [
                    x
                    for x in self.agent.crane_registrations
                    if body.location == x.location
                ]
                if body.dock_ids != None:
                    services = [x for x in services if x.dock_id in body.dock_ids]
                if body.transfer_point_ids != None:
                    services = [
                        x
                        for x in services
                        if x.transfer_point_id in body.transfer_point_ids
                    ]
            elif type(body) is TranstainerListQueryRefMsgBody():
                log(
                    f"Received transtainer list request for location {body.location} and transfer points {body.transfer_point_ids}"
                )
                services = [
                    x
                    for x in self.agent.transtainer_registrations
                    if body.location == x.location
                ]
                if body.transfer_point_ids != None:
                    services = [
                        x
                        for x in services
                        if x.transfer_point_id in body.transfer_point_ids
                    ]
            else:
                log("Received message with unknown body")
                return

            services_jids = [x.jid for x in services]
            await self.send(
                ServicesListInformMsgBody(services_jids).create_message(str(msg.sender))
            )
