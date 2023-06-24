from agents.loggingAgent import LoggingAgent
from spade.message import Message
from spade.behaviour import OneShotBehaviour
import datetime
from spade.message import Message
from spade.template import Template
from messageTemplates.yellowPagesAgentTemplates import (
    PortListRequestMsgBody,
    SERVICES_LIST_INFORM_TEMPLATE,
)
from messageTemplates.msgDecoder import decode_msg


class OperatorAgent(LoggingAgent):
    def __init__(
        self,
        jid: str,
        password: str,
        action: str,
        container_ids: list[str],
        date: datetime,
        location: str,
        yellow_pages_jid: str,
    ):
        super().__init__(jid, password)
        self.action = action
        self.container_ids = container_ids
        self.date = date
        self.location = location
        self.yellow_pages_jid = yellow_pages_jid

    async def setup(self):
        if self.action == "pickup":
            self.add_behaviour(
                self.RequestContainerBehaviour(),
                template=(SERVICES_LIST_INFORM_TEMPLATE),
            )
        elif self.action == "dropoff":
            self.add_behaviour(
                self.RegisterContainerBehaviour(),
                template=(SERVICES_LIST_INFORM_TEMPLATE),
            )
        else:
            raise ValueError("Unknown action")
        self.log("Operator agent started")

    async def get_port_list(self, parent_behaviour, location: str):
        log = parent_behaviour.agent.log

        portListRequest = PortListRequestMsgBody(parent_behaviour.agent.location)
        await parent_behaviour.send(
            portListRequest.create_message(parent_behaviour.agent.yellow_pages_jid)
        )

        portList = await parent_behaviour.receive(timeout=30)
        if portList is None:
            log("No port available. Shutting down ...")
            return None

        portList = decode_msg(portList).service_jids
        log(f"Port list received: {portList}")
        return portList

    class RequestContainerBehaviour(OneShotBehaviour):
        async def run(self):
            log = self.agent.log
            log(f"Requesting pick up of containers (on {self.agent.date}):")
            log(",".join(self.agent.container_ids))

            portList = await self.agent.get_port_list(self, self.agent.location)

            self.kill(exit_code=0)

    class RegisterContainerBehaviour(OneShotBehaviour):
        async def run(self):
            log = self.agent.log
            log(f"Requesting drop off of containers (on {self.agent.date}):")
            log(",".join(self.agent.container_ids))

            portList = await self.agent.get_port_list(self, self.agent.location)

            self.kill(exit_code=0)
