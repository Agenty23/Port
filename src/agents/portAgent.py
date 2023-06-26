from agents.loggingAgent import LoggingAgent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from messageTemplates.agentRegistration import (
    REGISTER_AGREE_TEMPLATE,
    REGISTER_REFUSE_TEMPLATE,
    PortRegistrationRequestMsgBody,
)
from messageTemplates.servicesListRequest import (
    SERVICES_LIST_INFORM_TEMPLATE,
    CraneListQueryRefMsgBody,
)
from messageTemplates.containerArrival import (
    CONTAINER_ARRIVAL_CFP_TEMPLATE,
    CONTAINER_ARRIVAL_PROPOSE_TEMPLATE,
    CONTAINER_ARRIVAL_REFUSE_TEMPLATE,
    CONTAINER_ARRIVAL_REJECT_PROPOSAL_TEMPLATE,
    CONTAINER_ARRIVAL_ACCEPT_PROPOSAL_TEMPLATE,
    ContainerArrivalCFPMsgBody,
    ContainerArrivalRefuseMsgBody,
    ContainerArrivalProposeMsgBody,
    ContainerArrivalRejectProposalMsgBody,
    ContainerArrivalAcceptProposalMsgBody,
)
from messageTemplates.msgDecoder import decode_msg
from datetime import datetime, timedelta
from typing import Union
from aioxmpp import JID
from logic.portCost import calculatePortCost


class PortAgent(LoggingAgent):
    # region Agent setup and registration
    def __init__(self, jid: str, password: str, location: str, yellow_pages_jid: str):
        """
        Creates a port agent instance.

        Args:
            jid (str): Port agent's JID.
            password (str): Port agent's password.
            location (str): Port agent's location.
            yellow_pages_jid (str): Yellow pages agent's JID.
        """
        super().__init__(jid, password)
        self.location = location
        self.yellow_pages_jid = yellow_pages_jid

    async def setup(self) -> None:
        self.add_behaviour(
            self.RegisterBehav(),
            template=(REGISTER_AGREE_TEMPLATE() | REGISTER_REFUSE_TEMPLATE()),
        )
        self.log("Port agent started")

    class RegisterBehav(OneShotBehaviour):
        def __init__(self):
            """Behaviour that registers port agent in yellow pages agent, and shuts down in case of failure."""
            super().__init__()

        async def run(self) -> None:
            self.agent: PortAgent
            log = self.agent.log
            body = PortRegistrationRequestMsgBody(self.agent.jid, self.agent.location)

            await self.send(body.create_message(self.agent.yellow_pages_jid))
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

        async def on_end(self) -> None:
            self.agent: PortAgent
            self.agent.add_behaviour(
                self.agent.ContainerArrivalCFPBehav(),
                template=(
                    CONTAINER_ARRIVAL_CFP_TEMPLATE() | SERVICES_LIST_INFORM_TEMPLATE()
                ),
            )

    # endregion

    # region Utility methods
    async def get_cranes_list(self, parent_behaviour: object) -> list[str]:
        """Sends request to yellow pages agent for cranes list in the port location"""
        cranes_list_request = CraneListQueryRefMsgBody(self.location)
        await parent_behaviour.send(
            cranes_list_request.create_message(self.yellow_pages_jid)
        )

        cranes_list = await parent_behaviour.receive(timeout=30)
        if cranes_list is None:
            return None

        cranes_list = decode_msg(cranes_list).service_jids
        return cranes_list

    # endregion

    # region Container arrival behaviours
    class ContainerArrivalCFPBehav(CyclicBehaviour):
        def __init__(self):
            """Behaviour handling container arrival CFPs from operators."""
            super().__init__()

        async def run(self) -> None:
            self.agent: PortAgent
            log = self.agent.log
            cfp = await self.receive(timeout=100)
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

            cranes_list = await self.agent.get_cranes_list(self)
            if not cranes_list:
                log("No cranes available")
                self.send(
                    ContainerArrivalRefuseMsgBody().create_message(
                        cfp.sender, thread=cfp.thread
                    )
                )
                return

            crane_cfp = ContainerArrivalCFPMsgBody(
                cfp_body.container_ids, cfp_body.date
            )
            for crane in cranes_list:
                await self.send(
                    crane_cfp.create_message(
                        crane, cfp_reply_by - timedelta(seconds=10), cfp.thread
                    )
                )

            self.agent.add_behaviour(
                self.agent.ContainerArrivalProposalBehav(
                    cfp.sender,
                    cfp_reply_by,
                    cfp.thread,
                    cfp_body.container_ids,
                    cfp_body.date,
                    len(cranes_list),
                ),
                template=(
                    CONTAINER_ARRIVAL_PROPOSE_TEMPLATE(cfp.thread)
                    | CONTAINER_ARRIVAL_REFUSE_TEMPLATE(cfp.thread)
                ),
            )

    class ContainerArrivalProposalBehav(OneShotBehaviour):
        def __init__(
            self,
            operator_jid: Union[JID, str],
            reply_by: datetime,
            thread: str,
            container_ids: list[str],
            date: datetime,
            max_responses: int,
        ):
            """
            Behaviour handling container arrival proposals and refuses from cranes.

            Args:
                operator_jid (str): Operator's JID who requested container arrival.
                reply_by (datetime): Time by which the operator should receive all proposals.
                thread (str): Thread ID of the conversation.
                container_ids (list[str]): List of arriving containers IDs.
                date (datetime): Estimated arrival date.
                max_responses (int): Maximum number of proposals/refuses to wait for.
            """
            super().__init__()
            self.operator_jid = operator_jid
            self.reply_by = reply_by
            self.thread = thread
            self.container_ids = container_ids
            self.date = date
            self.max_responses = max_responses


        async def run(self) -> None:
            self.agent: PortAgent
            log = self.agent.log

            crane_proposals = {}
            responses_received = 0
            reply_by = datetime.now() + timedelta(seconds=60)
            while (
                responses_received < self.max_responses
                and datetime.now() < self.reply_by
            ):
                response = await self.receive(timeout=10)
                if not response:
                    continue

                response_reply_by = datetime.fromisoformat(
                    response.get_metadata("reply-by")
                )

                response_body = decode_msg(response)
                if not response_body:
                    log("Invalid message")
                    continue

                if datetime.now() + timedelta(seconds=10) > response_reply_by:
                    log("Not enough time to process")
                    responses_received += 1
                    continue

                if isinstance(response_body, ContainerArrivalProposeMsgBody):
                    log(f"Received container arrival proposal from [{response.sender}]")
                    responses_received += 1
                    crane_proposals[response.sender] = response_body
                    reply_by = min(reply_by, response_reply_by)
                elif isinstance(response_body, ContainerArrivalRefuseMsgBody):
                    log(f"Received container arrival refuse from [{response.sender}]")
                    responses_received += 1
                else:
                    log("Unexpected message")

            if not crane_proposals:
                log("No proposals received")
                self.send(
                    ContainerArrivalRefuseMsgBody().create_message(
                        self.operator_jid, thread=self.thread
                    )
                )
                return

            (
                port_cost,
                accepted_containers_count,
                accepted_cranes,
            ) = calculatePortCost(self.date, crane_proposals)

            log(
                f"Able to accept {accepted_containers_count} containers with cost {port_cost}. Sending container arrival proposal to [{self.operator_jid}]."
            )
            self.send(
                ContainerArrivalProposeMsgBody(
                    port_cost,
                    accepted_containers_count,
                ).create_message(
                    self.operator_jid,
                    reply_by=reply_by - timedelta(seconds=10),
                    thread=self.thread,
                )
            )

            for crane in crane_proposals.keys():
                if str(crane) not in accepted_cranes:
                    self.send(
                        ContainerArrivalRejectProposalMsgBody().create_message(
                            crane, thread=self.thread
                        )
                    )

            if accepted_containers_count > 0:
                self.agent.add_behaviour(
                    self.agent.ContainerArrivalAcceptProposalBehav(
                        self.thread, reply_by, accepted_cranes
                    ),
                    template=(
                        CONTAINER_ARRIVAL_ACCEPT_PROPOSAL_TEMPLATE(self.thread)
                        | CONTAINER_ARRIVAL_REJECT_PROPOSAL_TEMPLATE(self.thread)
                    ),
                )

    class ContainerArrivalAcceptProposalBehav(OneShotBehaviour):
        def __init__(
            self,
            thread: str,
            reply_by: Union[datetime, str],
            accepted_cranes: list[str],
        ):
            """
            Behaviour handling container arrival proposal acceptance / rejection from operator.

            Args:
                thread (str): Thread ID of the conversation.
                reply_by (datetime | str): Time by which the operator should accept the proposal.
                accepted_cranes (list[str]): List of cranes that will realize the proposal.
            """
            super().__init__()
            self.thread = thread
            self.reply_by = reply_by
            self.accepted_cranes = accepted_cranes

        async def run(self) -> None:
            self.agent: PortAgent
            log = self.agent.log

            while datetime.now() < self.reply_by:
                proposal_response = await self.receive(timeout=1)
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
                    proposal_response_body, ContainerArrivalAcceptProposalMsgBody
                ):
                    log("Proposal accepted")
                    proposal_accepted = True
                elif isinstance(
                    proposal_response_body, ContainerArrivalRejectProposalMsgBody
                ):
                    log("Proposal rejected")
                else:
                    log("Unexpected message")

            if proposal_accepted:
                crane_reply = ContainerArrivalAcceptProposalMsgBody()
            else:
                crane_reply = ContainerArrivalRejectProposalMsgBody()

            for crane in self.accepted_cranes:
                self.send(crane_reply.create_message(crane, thread=self.thread))

    # endregion
