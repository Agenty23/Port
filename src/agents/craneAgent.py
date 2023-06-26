from agents.loggingAgent import LoggingAgent
from spade.behaviour import (
    CyclicBehaviour,
    OneShotBehaviour,
)
from messageTemplates.agentRegistration import (
    CraneRegistrationRequestMsgBody,
    REGISTER_AGREE_TEMPLATE,
    REGISTER_REFUSE_TEMPLATE,
)
from messageTemplates.servicesListRequest import (
    SERVICES_LIST_INFORM_TEMPLATE,
    TranstainerListQueryRefMsgBody,
)
from messageTemplates.containerArrival import (
    CONTAINER_ARRIVAL_CFP_TEMPLATE,
    CONTAINER_ARRIVAL_PROPOSE_TEMPLATE,
    CONTAINER_ARRIVAL_REFUSE_TEMPLATE,
    CONTAINER_ARRIVAL_ACCEPT_PROPOSAL_TEMPLATE,
    CONTAINER_ARRIVAL_REJECT_PROPOSAL_TEMPLATE,
    ContainerArrivalCFPMsgBody,
    ContainerArrivalProposeMsgBody,
    ContainerArrivalRefuseMsgBody,
    ContainerArrivalRejectProposalMsgBody,
    ContainerArrivalAcceptProposalMsgBody,
)
from messageTemplates.msgDecoder import decode_msg
from datetime import datetime, timedelta
from time import time
from logic.craneCost import calculateCraneCost
from typing import Union
from aioxmpp import JID


class CraneAgent(LoggingAgent):
    # region Agent setup and registration
    def __init__(
        self,
        jid: str,
        password: str,
        location: str,
        docks_ids: list[int],
        transfer_points_ids: list[int],
        yellow_pages_jid: str,
    ):
        """
        Creates a crane agent instance.

        Args:
            jid (str): Crane agent's JID.
            password (str): Crane agent's password.
            location (str): Crane agent's location.
            docks_ids (list[int]): List of docks ids that crane agent can serve.
            transfer_points_ids (list[int]): List of transfer points ids that crane agent can serve.
            yellow_pages_jid (str): Yellow pages agent's JID.
        """
        super().__init__(jid, password)
        self.location = location
        self.docks_ids = docks_ids
        self.transfer_points_ids = transfer_points_ids
        self.yellow_pages_jid = yellow_pages_jid

    async def setup(self):
        self.add_behaviour(
            self.RegisterBehav(),
            template=(REGISTER_AGREE_TEMPLATE() | REGISTER_REFUSE_TEMPLATE()),
        )
        self.log("Crane agent started")

    class RegisterBehav(OneShotBehaviour):
        def __init__(self):
            """Behaviour that registers crane agent in yellow pages agent, and shuts down in case of failure."""
            super().__init__()

        async def run(self):
            self.agent: CraneAgent
            log = self.agent.log
            body = CraneRegistrationRequestMsgBody(
                str(self.agent.jid),
                self.agent.location,
                self.agent.docks_ids,
                self.agent.transfer_points_ids,
            )

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
                else:
                    log("Unexpected reply")

            log("Failed to register. Shutting down...")
            self.kill()

        async def on_end(self):
            self.agent.add_behaviour(
                self.agent.ContainerArrivalCFPBehav(),
                template=(
                    CONTAINER_ARRIVAL_CFP_TEMPLATE() | SERVICES_LIST_INFORM_TEMPLATE()
                ),
            )

    # endregion

    # region Utility methods
    async def get_transtainers_list(self, parent_behaviour) -> list[str]:
        """Sends request to yellow pages agent for transtainers list."""
        transtainers_list_request = TranstainerListQueryRefMsgBody(
            self.location, self.transfer_points_ids
        )
        await parent_behaviour.send(
            transtainers_list_request.create_message(self.yellow_pages_jid)
        )

        transtainers_list = await parent_behaviour.receive(timeout=30)
        if transtainers_list is None:
            return None

        transtainers_list = decode_msg(transtainers_list).service_jids
        return transtainers_list

    # endregion

    # region Container arrival behaviours
    class ContainerArrivalCFPBehav(CyclicBehaviour):
        def __init__(self):
            """Behaviour handling container arrival CFPs from port."""
            super().__init__()

        async def run(self) -> None:
            self.agent: CraneAgent
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

            transtainer_list = await self.agent.get_transtainers_list(self)
            if not transtainer_list:
                log("No transtainers available")
                await self.send(
                    ContainerArrivalRefuseMsgBody().create_message(
                        cfp.sender, thread=cfp.thread
                    )
                )
                return

            transtainer_cfp = ContainerArrivalCFPMsgBody(
                cfp_body.container_ids, cfp_body.date
            )
            for transtainer in transtainer_list:
                await self.send(
                    transtainer_cfp.create_message(
                        transtainer, cfp_reply_by - timedelta(seconds=10), cfp.thread
                    )
                )

            self.agent.add_behaviour(
                self.agent.ContainerArrivalProposalBehav(
                    cfp.sender,
                    cfp_reply_by,
                    cfp.thread,
                    cfp_body.container_ids,
                    cfp_body.date,
                    len(transtainer_list),
                ),
                template=(
                    CONTAINER_ARRIVAL_PROPOSE_TEMPLATE(cfp.thread)
                    | CONTAINER_ARRIVAL_REFUSE_TEMPLATE(cfp.thread)
                ),
            )

    class ContainerArrivalProposalBehav(OneShotBehaviour):
        def __init__(
            self,
            port_jid: Union[JID, str],
            reply_by: datetime,
            thread: str,
            container_ids: list[str],
            date: datetime,
            max_responses: int,
        ):
            """
            Behaviour handling container arrival proposals and refuses from transtainers.

            Args:
                port_jid (JID | str): Port's JID who sent CFP.
                reply_by (datetime): Time by which all proposals should be received.
                thread (str): Thread ID of the conversation.
                container_ids (list[str]): List of arriving containers IDs.
                date (datetime): Estimated arrival date.
                max_responses (int): Maximum number of responses expected.
            """
            self.port_jid = port_jid
            self.reply_by = reply_by
            self.thread = thread
            self.container_ids = container_ids
            self.date = date
            self.max_responses = max_responses

        async def run(self) -> None:
            self.agent: CraneAgent
            log = self.agent.log

            transtainer_proposals = {}
            responses_received = 0
            reply_by = self.reply_by + timedelta(seconds=60)
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
                    transtainer_proposals[response.sender] = response_body
                    reply_by = min(reply_by, response_reply_by)
                elif isinstance(response_body, ContainerArrivalRefuseMsgBody):
                    log(f"Received container arrival refuse from [{response.sender}]")
                    responses_received += 1
                else:
                    log("Unexpected message")

            if not transtainer_proposals:
                log("No proposals received")
                self.send(
                    ContainerArrivalRefuseMsgBody().create_message(
                        self.port_jid, thread=self.thread
                    )
                )
                return

            (
                crane_cost,
                accepted_containers_count,
                accepted_transtainers,
            ) = calculateCraneCost(self.date, transtainer_proposals)

            log(
                f"Able to accept {accepted_containers_count} containers with cost {crane_cost}. Sending container arrival proposal to [{self.port_jid}]."
            )
            self.send(
                ContainerArrivalProposeMsgBody(
                    crane_cost,
                    accepted_containers_count,
                ).create_message(
                    self.port_jid,
                    reply_by=reply_by - timedelta(seconds=10),
                    thread=self.thread,
                )
            )

            for crane in transtainer_proposals.keys():
                if str(crane) not in accepted_transtainers:
                    self.send(
                        ContainerArrivalRejectProposalMsgBody().create_message(
                            crane, thread=self.thread
                        )
                    )

            if accepted_containers_count > 0:
                self.agent.add_behaviour(
                    self.agent.ContainerArrivalAcceptProposalBehav(
                        self.thread, reply_by, accepted_transtainers
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
            accepted_transtainers: list[str],
        ):
            """
            Behaviour handling container arrival proposal acceptances / rejections from port agent.

            Args:
                thread (str): Thread ID of the conversation.
                reply_by (datetime | str): Time by which all responses should be received.
                accepted_transtainers (list[str]): List of transtainers that will realize the proposal.
            """
            self.thread = thread
            self.reply_by = reply_by
            self.accepted_transtainers = accepted_transtainers

        async def run(self) -> None:
            self.agent: CraneAgent
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
                transtainer_reply = ContainerArrivalAcceptProposalMsgBody()
            else:
                transtainer_reply = ContainerArrivalRejectProposalMsgBody()

            for transtainer in self.accepted_transtainers:
                self.send(
                    transtainer_reply.create_message(transtainer, thread=self.thread)
                )

    # endregion
