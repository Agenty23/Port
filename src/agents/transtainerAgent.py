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
from time import time
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
import numpy as np
from typing import Optional
from logic.transtainerCost import (
    calculateTranstainerOutCost,
    calculateTranstainerInCost,
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
            cost, containers_placement = calculateTranstainerInCost(
                self.agent.yard, cfp_body.date, container_count
            )
            proposal_reply_by = datetime.now() + timedelta(seconds=60)

            log(f"Proposing cost: {cost} for {container_count} containers")
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
                    self.agent.yard = rearrangeYard(
                        self.agent.yard, self.containers_placement
                    )
                elif isinstance(msg_body, ContainerArrivalRejectProposalMsgBody):
                    log("Proposal rejected")
                else:
                    log("Unexpected message")

    # endregion

    class ContainerDepartureCFPBehaviour(CyclicBehaviour):
        async def run(self):
            log = self.agent.log
            msg = await self.receive(timeout=30)
            if not msg:
                return

            log(f"Received container departure CFP from [{msg.sender}]")
            body = decode_msg(msg)
            if not body:
                log("Invalid message")
                return

            msg_reply_by = datetime.fromisoformat(msg.get_metadata("reply-by"))
            if msg_reply_by < datetime.now() + timedelta(seconds=10):
                log("Not enough time to process")
                return

            local_containers = []
            for container in body.container_ids:
                if container in self.agent.containers:
                    local_containers.append(container)

            if not local_containers:
                log("No containers")
                await self.send(
                    ContainerArrivalRefuseMsgBody().create_message(  # TODO: change to departure refuse
                        msg.sender, msg.thread
                    )
                )
                return

            cost = calculateTranstainerOutCost(self.agent.yard, local_containers)
            log(f"Proposing cost: {cost} for containers: {local_containers}")
            await self.send(
                ContainerArrivalProposeMsgBody(
                    cost, local_containers
                ).create_message(  # TODO: change to departure propose
                    msg.sender, msg.thread
                )
            )
