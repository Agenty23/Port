from messageTemplates.msgBody import MsgBody
from spade.template import Template
from datetime import datetime
from uuid import uuid4, UUID

# CFP template (operator -> port | port -> crane | crane -> transtainer)
CONTAINER_ARRIVAL_CFP_TEMPLATE = Template()
CONTAINER_ARRIVAL_CFP_TEMPLATE.set_metadata("performative", "cfp")
CONTAINER_ARRIVAL_CFP_TEMPLATE.set_metadata("topic", "container_arrival")


# CFP message (operator -> port | port -> crane | crane -> transtainer)
class ContainerArrivalCFPMsgBody(MsgBody):
    def __init__(self, container_ids: list[str], date: datetime):
        self.container_ids = container_ids
        self.date = date

    def create_message(self, to: str, reply_by: datetime, thread: UUID):
        msg = super().create_message(to)
        msg.set_metadata("performative", "cfp")
        msg.set_metadata("topic", "container_arrival")
        msg.set_reply_by(reply_by)
        if thread is None:
            thread = uuid4()
        msg.set_thread(thread)
        return msg


# Refuse template (transtainer -> crane | crane -> port | port -> operator)
CONTAINER_ARRIVAL_REFUSE_TEMPLATE = Template()
CONTAINER_ARRIVAL_REFUSE_TEMPLATE.set_metadata("performative", "refuse")
CONTAINER_ARRIVAL_REFUSE_TEMPLATE.set_metadata("topic", "container_arrival")


# Refuse message (transtainer -> crane | crane -> port | port -> operator)
class ContainerArrivalRefuseMsgBody(MsgBody):
    def create_message(self, to: str, thread: UUID):
        msg = super().create_message(to)
        msg.set_metadata("performative", "refuse")
        msg.set_metadata("topic", "container_arrival")
        msg.set_thread(thread)
        return msg


# Propose template (transtainer -> crane | crane -> port | port -> operator)
CONTAINER_ARRIVAL_PROPOSE_TEMPLATE = Template()
CONTAINER_ARRIVAL_PROPOSE_TEMPLATE.set_metadata("performative", "propose")
CONTAINER_ARRIVAL_PROPOSE_TEMPLATE.set_metadata("topic", "container_arrival")


# Propose message (transtainer -> crane | crane -> port | port -> operator)
class ContainerArrivalProposeMsgBody(MsgBody):
    def __init__(self, cost: float):
        self.cost = cost

    def create_message(self, to: str, thread: UUID):
        msg = super().create_message(to)
        msg.set_metadata("performative", "propose")
        msg.set_metadata("topic", "container_arrival")
        msg.set_thread(thread)
        return msg


# Reject proposal template (crane -> transtainer | port -> crane | operator -> port)
CONTAINER_ARRIVAL_REJECT_PROPOSAL_TEMPLATE = Template()
CONTAINER_ARRIVAL_REJECT_PROPOSAL_TEMPLATE.set_metadata(
    "performative", "reject-proposal"
)
CONTAINER_ARRIVAL_REJECT_PROPOSAL_TEMPLATE.set_metadata("topic", "container_arrival")


# Reject proposal message (crane -> transtainer | port -> crane | operator -> port)
class ContainerArrivalRejectProposalMsgBody(MsgBody):
    def create_message(self, to: str, thread: UUID):
        msg = super().create_message(to)
        msg.set_metadata("performative", "reject-proposal")
        msg.set_metadata("topic", "container_arrival")
        msg.set_thread(thread)
        return msg


# Accept proposal template (crane -> transtainer | port -> crane | operator -> port)
CONTAINER_ARRIVAL_ACCEPT_PROPOSAL_TEMPLATE = Template()
CONTAINER_ARRIVAL_ACCEPT_PROPOSAL_TEMPLATE.set_metadata(
    "performative", "accept-proposal"
)
CONTAINER_ARRIVAL_ACCEPT_PROPOSAL_TEMPLATE.set_metadata("topic", "container_arrival")


# Accept proposal message (crane -> transtainer | port -> crane | operator -> port)
class ContainerArrivalAcceptProposalMsgBody(MsgBody):
    def create_message(self, to: str, thread: UUID):
        msg = super().create_message(to)
        msg.set_metadata("performative", "accept-proposal")
        msg.set_metadata("topic", "container_arrival")
        msg.set_thread(thread)
        return msg
