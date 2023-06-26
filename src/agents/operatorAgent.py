from agents.loggingAgent import LoggingAgent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from datetime import datetime, timedelta
from messageTemplates.servicesListRequest import (
    SERVICES_LIST_INFORM_TEMPLATE,
    PortListQueryRefMsgBody,
)
from messageTemplates.msgDecoder import decode_msg
from messageTemplates.containerArrival import (
    ContainerArrivalCFPMsgBody,
    CONTAINER_ARRIVAL_PROPOSE_TEMPLATE,
    CONTAINER_ARRIVAL_REFUSE_TEMPLATE,
    ContainerArrivalAcceptProposalMsgBody,
    ContainerArrivalRejectProposalMsgBody,
    ContainerArrivalProposeMsgBody,
    ContainerArrivalRefuseMsgBody,
)
from uuid import uuid4
from enum import Enum


class OperatorAgentAction(Enum):
    PICKUP = 1
    DROPOFF = 2


class OperatorAgent(LoggingAgent):
    # region Agent setup
    def __init__(
        self,
        jid: str,
        password: str,
        action: OperatorAgentAction,
        container_ids: list[str],
        date: datetime,
        location: str,
        yellow_pages_jid: str,
    ) -> None:
        """
        Creates an operator agent instance, which requests one action to be performed by the port.
        It can be either pickup or dropoff of containers.

        Args:
            jid (str): Operator agent's JID.
            password (str): Operator agent's password.
            action (OperatorAgentAction): Action to be performed by the port (PICKUP or DROPOFF).
            container_ids (list[str]): List of container IDs to be picked up or dropped off.
            date (datetime): Estimated date of the action.
            location (str): Location of the port where the action should be performed.
            yellow_pages_jid (str): Yellow pages agent's JID.
        """
        super().__init__(jid, password)
        self.action = action
        self.container_ids = container_ids
        self.date = date
        self.location = location
        self.yellow_pages_jid = yellow_pages_jid

    async def setup(self) -> None:
        if self.action is OperatorAgentAction.PICKUP:
            self.add_behaviour(
                self.PickupContainerBehav(),
                template=(
                    SERVICES_LIST_INFORM_TEMPLATE()
                    #TODO
                ),
            )
        elif self.action is OperatorAgentAction.DROPOFF:
            self.add_behaviour(
                self.DropoffContainerBehav(),
                template=(
                    SERVICES_LIST_INFORM_TEMPLATE()
                    | CONTAINER_ARRIVAL_PROPOSE_TEMPLATE()
                    | CONTAINER_ARRIVAL_REFUSE_TEMPLATE()
                ),
            )
        else:
            raise ValueError("Unknown action")
        self.log("Operator agent started")

    # endregion

    async def get_port_list(self, parent_behaviour, location: str) -> list[str]:
        """
        Sends a request for a list of ports available at the given location.

        Args:
            parent_behaviour (Behaviour): Behaviour that is sending the request.
            location (str): Location of the port.
        """
        log = parent_behaviour.agent.log

        await parent_behaviour.send(
            PortListQueryRefMsgBody(location).create_message(self.yellow_pages_jid)
        )

        port_list = await parent_behaviour.receive(timeout=30)
        if port_list is None:
            log("No port available.")
            return None

        port_list = decode_msg(port_list).service_jids
        log(f"Port list received: {port_list}")
        return port_list

    class PickupContainerBehav(OneShotBehaviour):
        def __init__(self):
            """Behaviour that requests departure of given containers."""
            super().__init__()

        async def run(self) -> None:
            self.agent: OperatorAgent
            log = self.agent.log
            log(f"Requesting pick up of containers (on {self.agent.date}):")
            log(str(self.agent.container_ids))

            port_list = await self.agent.get_port_list(self, self.agent.location)
            if port_list is None:
                log("No port available.")
                return

            reply_by = datetime.now() + timedelta(seconds=60)
            # TODO

        async def on_end(self) -> None:
            self.agent: OperatorAgent
            self.agent.log("Shutting down ...")
            await self.agent.stop()

    class DropoffContainerBehav(OneShotBehaviour):
        def __init__(self):
            """Behaviour that requests arrival of given containers."""
            super().__init__()

        async def run(self) -> None:
            self.agent: OperatorAgent
            log = self.agent.log
            log(f"Requesting container arrival of containers (on {self.agent.date}):")
            log(",".join(self.agent.container_ids))

            port_list = await self.agent.get_port_list(self, self.agent.location)
            if port_list is None:
                log("No port available.")
                return

            reply_by = datetime.now() + timedelta(seconds=120)
            cfp = ContainerArrivalCFPMsgBody(self.agent.container_ids, self.agent.date)
            thread = uuid4().hex
            for port in port_list:
                await self.send(
                    cfp.create_message(port, reply_by=reply_by, thread=thread)
                )
                log(f"Container arrival CFP sent to port [{port}].")

            log(f"Waiting for responses till {reply_by} ...")
            cost_port_map = {}
            while datetime.now() <= reply_by:
                if (reply := await self.receive(timeout=1)) is not None:
                    reply_body = decode_msg(reply)

                    if reply.thread != thread or reply_body is None:
                        log(f"Unexpected message from {reply.sender}")
                    elif isinstance(reply_body, ContainerArrivalProposeMsgBody):
                        log(f"Container arrival proposition from [{reply.sender}]")
                        cost_port_map[str(reply.sender)] = reply_body.cost
                        break
                    elif isinstance(reply_body, ContainerArrivalRefuseMsgBody):
                        log(f"Container arrival refused by [{reply.sender}]")
                        break
                    else:
                        log(f"Unexpected message from {reply.sender}")

            if len(cost_port_map) == 0:
                log("No port accepted the request.")
                return

            min_cost_port = min(cost_port_map, key=cost_port_map.get)
            log(
                f"Container arrival proposition from {min_cost_port} with cost {cost_port_map[min_cost_port]} accepted"
            )
            await self.send(
                ContainerArrivalAcceptProposalMsgBody().create_message(
                    min_cost_port, thread=thread
                )
            )

            for port in cost_port_map:
                if port != min_cost_port:
                    await self.send(
                        ContainerArrivalRejectProposalMsgBody().create_message(
                            port, thread=thread
                        )
                    )

        async def on_end(self) -> None:
            self.agent: OperatorAgent
            self.agent.log("Shutting down ...")
            await self.agent.stop()
