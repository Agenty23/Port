from agents.loggingAgent import LoggingAgent
from spade.behaviour import (
    OneShotBehaviour,
    CyclicBehaviour,
)
from messageTemplates.agentRegistration import (
    REGISTER_AGREE_TEMPLATE,
    REGISTER_REFUSE_TEMPLATE,
    TranstainerRegistrationRequestMsgBody,
)
from messageTemplates.servicesListRequest import (
    SERVICES_LIST_INFORM_TEMPLATE,
    CraneListQueryRefMsgBody,
)
from messageTemplates.msgDecoder import decode_msg
from datetime import datetime, timedelta
from messageTemplates.containerArrival import (
    CONTAINER_ARRIVAL_CFP_TEMPLATE,
    CONTAINER_ARRIVAL_ACCEPT_PROPOSAL_TEMPLATE,
    CONTAINER_ARRIVAL_REJECT_PROPOSAL_TEMPLATE,
    ContainerArrivalProposeMsgBody,
    ContainerArrivalRefuseMsgBody,
    ContainerArrivalAcceptProposalMsgBody,
    ContainerArrivalRejectProposalMsgBody,
)
from messageTemplates.containerDeparture import (
    CONTAINER_DEPARTURE_CFP_TEMPLATE,
    CONTAINER_DEPARTURE_PROPOSE_TEMPLATE,
    CONTAINER_DEPARTURE_REFUSE_TEMPLATE,
    CONTAINER_DEPARTURE_ACCEPT_PROPOSAL_TEMPLATE,
    CONTAINER_DEPARTURE_REJECT_PROPOSAL_TEMPLATE,
    ContainerDepartureCFPMsgBody,
    ContainerDepartureRefuseMsgBody,
    ContainerDepartureProposeMsgBody,
    ContainerDepartureAcceptProposalMsgBody,
    ContainerDepartureRejectProposalMsgBody,
)
import numpy as np
from logic.transtainer import (
    calculateTranstainerArrivalCost,
    calculateTranstainerDepartureCost,
    rearrangeYard,
)
from typing import Union
from aioxmpp import JID


class TranstainerAgent(LoggingAgent):
    # region Agent setup and registration
    def __init__(
        self,
        jid: str,
        password: str,
        location: str,
        transfer_point_id: int,
        yellow_pages_jid: str,
        yard: np.ndarray = np.empty((5, 5, 5), dtype=str),
    ):
        """
        Creates a transtainer agent instance.

        Args:
            jid (str): Transtainer agent's JID.
            password (str): Transtainer agent's password.
            location (str): Transtainer agent's location.
            transfer_point_id (int): Transfer point ID that transtainer is assigned to.
            yellow_pages_jid (str): Yellow pages agent's JID.
            yard (np.ndarray): Transtainer agent's yard matrix.
        """
        super().__init__(jid, password)
        self.yellow_pages_jid = yellow_pages_jid
        self.location = location
        self.transfer_point_id = transfer_point_id
        self.yard = yard

    async def setup(self) -> None:
        self.add_behaviour(
            self.RegisterBehav(),
            template=(REGISTER_AGREE_TEMPLATE() | REGISTER_REFUSE_TEMPLATE()),
        )
        self.log("Transtainer agent started")

    class RegisterBehav(OneShotBehaviour):
        def __init__(self):
            """Behaviour that registers transtainer agent in the yellow pages, and shuts down if registration fails."""
            super().__init__()

        async def run(self) -> None:
            self.agent: TranstainerAgent
            log = self.agent.log
            body = TranstainerRegistrationRequestMsgBody(
                self.agent.jid,
                self.agent.location,
                self.agent.transfer_point_id,
            )

            await self.send(body.create_message(to=self.agent.yellow_pages_jid))
            log(
                f"Register request sent to yellow pages agent [{self.agent.yellow_pages_jid}]"
            )

            reply_by = datetime.now() + timedelta(seconds=30)
            while datetime.now() < reply_by:
                reply = await self.receive(timeout=(reply_by - datetime.now()).seconds)
                if not reply or str(reply.sender) != self.agent.yellow_pages_jid:
                    continue

                if REGISTER_AGREE_TEMPLATE().match(reply):
                    log("Registration accepted")
                    return
                elif REGISTER_REFUSE_TEMPLATE().match(reply):
                    log("Registration refused")
                    break
                else:
                    log("Unexpected reply")

            log("Failed to register. Shutting down...")
            self.agent.stop()

        async def on_end(self):
            self.agent: TranstainerAgent
            self.agent.add_behaviour(
                self.agent.ContainerArrivalCFPBehav(),
                template=(CONTAINER_ARRIVAL_CFP_TEMPLATE()),
            )
            self.agent.add_behaviour(
                self.agent.ContainerDepartureCFPBehav(),
                template=(
                    CONTAINER_DEPARTURE_CFP_TEMPLATE() | SERVICES_LIST_INFORM_TEMPLATE()
                ),
            )

    # endregion

    # region Utility methods
    async def get_cranes_list(self, parent_behaviour: object) -> list[str]:
        """Sends request to yellow pages agent for cranes list which can server transtainer"""
        cranes_list_request = CraneListQueryRefMsgBody(
            self.location, transfer_point_ids=[self.transfer_point_id]
        )
        await parent_behaviour.send(
            cranes_list_request.create_message(self.yellow_pages_jid)
        )

        cranes_list = await parent_behaviour.receive(timeout=30)
        if cranes_list is None:
            return None

        cranes_list = decode_msg(cranes_list).service_jids
        return cranes_list

    # endregion

    # region: Container arrival behaviour
    class ContainerArrivalCFPBehav(CyclicBehaviour):
        def __init__(self):
            """Behaviour handling container arrival CFPs from cranes."""
            super().__init__()

        async def run(self) -> None:
            self.agent: TranstainerAgent
            log = self.agent.log
            cfp = await self.receive(timeout=30)
            if not cfp:
                return

            log(f"Received container arrival CFP from [{cfp.sender}]")
            cfp_body = decode_msg(cfp)
            if not cfp_body:
                log("Invalid message")
                return

            cfp_reply_by = datetime.fromisoformat(cfp.get_metadata("reply-by"))
            if cfp_reply_by < datetime.now() + timedelta(seconds=10):
                log("Not enough time to process")
                return

            free_places = len([x for x in self.agent.yard.flatten() if x.strip() == ""])
            if free_places == 0:
                log("No free places")
                await self.send(
                    ContainerArrivalRefuseMsgBody().create_message(
                        cfp.sender, cfp.thread
                    )
                )
                return

            container_count = min(free_places, len(cfp_body.container_ids))
            cost, containers_placement = calculateTranstainerArrivalCost(
                self.agent.yard, cfp_body.date, container_count
            )
            proposal_reply_by = datetime.now() + timedelta(seconds=60)

            log(f"Proposing cost: {cost} for {container_count} containers.")
            await self.send(
                ContainerArrivalProposeMsgBody(cost, container_count).create_message(
                    cfp.sender, proposal_reply_by, cfp.thread
                ),
            )

            self.agent.add_behaviour(
                self.agent.ContainerArrivalAcceptProposalBehav(
                    cfp.thread, proposal_reply_by, containers_placement
                ),
                template=(
                    CONTAINER_ARRIVAL_ACCEPT_PROPOSAL_TEMPLATE(cfp.thread)
                    | CONTAINER_ARRIVAL_REJECT_PROPOSAL_TEMPLATE(cfp.thread)
                ),
            )

    class ContainerArrivalAcceptProposalBehav(CyclicBehaviour):
        def __init__(
            self,
            thread: str,
            reply_by: Union[datetime, str],
            containers_placement: dict[str, tuple[int, int, int]],
        ):
            """Behaviour handling container arrival proposal acceptance / rejection from cranes.

            Args:
                thread (str): Thread ID of the conversation.
                reply_by (datetime | str): Deadline for reply.
                containers_placement (dict[str, tuple[int, int, int]]): Placement of new containers in the yard if proposal is accepted.
            """
            super().__init__()
            self.thread = thread
            self.reply_by = reply_by
            self.containers_placement = containers_placement

        async def run(self) -> None:
            self.agent: TranstainerAgent
            log = self.agent.log

            while datetime.now() < self.reply_by:
                msg = await self.receive(
                    timeout=(self.reply_by - datetime.now()).seconds
                )
                if not msg:
                    continue

                msg_body = decode_msg(msg)
                if not msg_body:
                    log("Invalid message")
                    continue

                if isinstance(msg_body, ContainerArrivalAcceptProposalMsgBody):
                    log("Proposal accepted")
                    rearrangeYard(self.agent, self.containers_placement)
                elif isinstance(msg_body, ContainerArrivalRejectProposalMsgBody):
                    log("Proposal rejected")
                else:
                    log("Unexpected message")

    # endregion

    # region: Container departure behaviour
    class ContainerDepartureCFPBehav(CyclicBehaviour):
        def __init__(self):
            """Behaviour handling container departure CFPs from cranes."""
            super().__init__()

        async def run(self):
            self.agent: TranstainerAgent
            log = self.agent.log
            cfp = await self.receive(timeout=30)
            if not cfp:
                return

            log(f"Received container departure CFP from [{cfp.sender}]")
            cfp_body = decode_msg(cfp)
            if not cfp_body:
                log("Invalid message")
                return

            cfp_reply_by = datetime.fromisoformat(cfp.get_metadata("reply-by"))
            if cfp_reply_by < datetime.now() + timedelta(seconds=10):
                log("Not enough time to process")
                return

            if not any(
                [x in self.agent.yard.flatten() for x in cfp_body.container_ids]
            ):
                log("Containers not in yard")
                await self.send(
                    ContainerDepartureRefuseMsgBody().create_message(
                        cfp.sender, cfp.thread
                    )
                )
                return

            crane_list = await self.agent.get_cranes_list(self)
            if not crane_list:
                log("No cranes available")
                self.send(
                    ContainerDepartureRefuseMsgBody().create_message(
                        cfp.sender, cfp.thread
                    )
                )
                return

            container_cfp = ContainerDepartureCFPMsgBody(
                cfp_body.container_ids, cfp_body.date, self.agent.transfer_point_id
            )
            for crane in crane_list:
                await self.send(
                    container_cfp.create_message(
                        crane, cfp_reply_by - timedelta(seconds=10), cfp.thread
                    )
                )

            self.agent.add_behaviour(
                self.agent.ContainerDepartureProposalBehav(
                    cfp.sender,
                    cfp_reply_by,
                    cfp.thread,
                    cfp_body.container_ids,
                    cfp_body.date,
                    len(crane_list),
                ),
                template=(
                    CONTAINER_DEPARTURE_PROPOSE_TEMPLATE(cfp.thread)
                    | CONTAINER_DEPARTURE_REFUSE_TEMPLATE(cfp.thread)
                ),
            )

    class ContainerDepartureProposalBehav(OneShotBehaviour):
        def __init__(
            self,
            port_jid: str,
            reply_by: datetime,
            thread: str,
            container_ids: list[str],
            date: datetime,
            max_responses: int,
        ):
            """
            Behaviour handling container departure proposal from cranes.

            Args:
                port_jid (str): JID of the port agent.
                reply_by (datetime): Deadline for reply.
                thread (str): Thread ID of the conversation.
                container_ids (list[str]): List of container IDs to be loaded.
                date (datetime): Estimated date of departure.
                max_responses (int): Maximum number of responses to wait for.
            """
            super().__init__()
            self.port_jid = port_jid
            self.reply_by = reply_by
            self.thread = thread
            self.container_ids = container_ids
            self.date = date
            self.max_responses = max_responses

        async def run(self) -> None:
            self.agent: TranstainerAgent
            log = self.agent.log

            crane_proposals: dict[str, ContainerDepartureProposeMsgBody] = {}
            responses_received = 0
            reply_by = datetime.now() + timedelta(seconds=60)
            while (
                responses_received < self.max_responses
                and datetime.now() < self.reply_by
            ):
                response = await self.receive(
                    timeout=(self.reply_by - datetime.now()).seconds
                )
                if not response:
                    continue

                response_body = decode_msg(response)
                if not response_body:
                    log("Invalid message")
                    continue

                if datetime.now() + timedelta(seconds=10) > self.reply_by:
                    log("Not enough time to process")
                    responses_received += 1
                    continue

                if isinstance(response_body, ContainerDepartureProposeMsgBody):
                    log(
                        f"Received container departure proposal from [{response.sender}]"
                    )
                    responses_received += 1
                    crane_proposals[str(response.sender)] = response_body
                    response_reply_by = datetime.fromisoformat(
                        response.get_metadata("reply-by")
                    )
                    reply_by = min(reply_by, response_reply_by)
                elif isinstance(response_body, ContainerDepartureRefuseMsgBody):
                    log(
                        f"Received container departure refusal from [{response.sender}]"
                    )
                    responses_received += 1
                else:
                    log("Unexpected message")

            if not crane_proposals:
                log("No proposals received")
                await self.send(
                    ContainerDepartureRejectProposalMsgBody().create_message(
                        self.port_jid, thread=self.thread
                    )
                )
                return

            container_ids = [
                container_id
                for container_id in self.agent.yard.flatten()
                if container_id in self.container_ids
            ]
            transtainer_cost = calculateTranstainerDepartureCost(
                self, self.date, container_ids, crane_proposals
            )

            log(f"Sending container departure proposal to [{self.port_jid}]")
            await self.send(
                ContainerDepartureProposeMsgBody(
                    transtainer_cost, container_ids
                ).create_message(self.port_jid, reply_by, self.thread)
            )

            self.agent.add_behaviour(
                self.agent.ContainerDepartureAcceptProposalBehav(
                    self.thread, reply_by, list(crane_proposals.keys())
                ),
                template=(
                    CONTAINER_DEPARTURE_ACCEPT_PROPOSAL_TEMPLATE(self.thread)
                    | CONTAINER_DEPARTURE_REJECT_PROPOSAL_TEMPLATE(self.thread)
                ),
            )

    class ContainerDepartureAcceptProposalBehav(OneShotBehaviour):
        def __init__(self, thread: str, reply_by: datetime, cranes: list[str]):
            """
            Behaviour handling container departure proposal acceptance from port.

            Args:
                thread (str): Thread ID of the conversation.
                reply_by (datetime): Deadline for reply.
                cranes (list[str]): List of cranes to be used.
            """
            super().__init__()
            self.thread = thread
            self.reply_by = reply_by
            self.cranes = cranes

        async def run(self) -> None:
            self.agent: TranstainerAgent
            log = self.agent.log

            while datetime.now() < self.reply_by:
                proposal_response = await self.receive(
                    timeout=(self.reply_by - datetime.now()).seconds
                )
                if proposal_response:
                    break

            proposal_accepted = False

            if not proposal_response:
                log("No response received")
            else:
                proposal_response_body = decode_msg(proposal_response)
                if not proposal_response_body:
                    log("Invalid message")
                elif isinstance(
                    proposal_response_body, ContainerDepartureAcceptProposalMsgBody
                ):
                    log("Proposal accepted")
                    proposal_accepted = True
                elif isinstance(
                    proposal_response_body, ContainerDepartureRejectProposalMsgBody
                ):
                    log("Proposal rejected")
                else:
                    log("Unexpected message")

            if proposal_accepted:
                crane_reply = ContainerDepartureAcceptProposalMsgBody()
            else:
                crane_reply = ContainerDepartureRejectProposalMsgBody()

            for crane in self.cranes:
                await self.send(crane_reply.create_message(crane, thread=self.thread))

    # endregion
