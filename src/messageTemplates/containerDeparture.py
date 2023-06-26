from messageTemplates.msgBody import MsgBody
from spade.template import Template
from spade.message import Message
from datetime import datetime
from typing import Optional, Union
from aioxmpp import JID


def CONTAINER_DEPARTURE_CFP_TEMPLATE(thread: Optional[str] = None) -> Template:
    """
    Template for container departure CFP message.

    Args:
        thread (str, optional): Thread ID used for accepting only given conversation.

    Accepts:
        - ContainerDepartureCFPMsgBody
    """
    t = Template(thread=thread)
    t.set_metadata("performative", "cfp")
    t.set_metadata("topic", "container_departure")
    return t


def CONTAINER_DEPARTURE_REFUSE_TEMPLATE(thread: Optional[str] = None) -> Template:
    """
    Template for container departure refuse message.

    Args:
        thread (str, optional): Thread ID used for accepting only given conversation.

    Accepts:
        - ContainerDepartureRefuseMsgBody
    """
    t = Template(thread=thread)
    t.set_metadata("performative", "refuse")
    t.set_metadata("topic", "container_departure")
    return t


def CONTAINER_DEPARTURE_PROPOSE_TEMPLATE(thread: Optional[str] = None) -> Template:
    """
    Template for container departure propose message.

    Args:
        thread (str, optional): Thread ID used for accepting only given conversation.

    Accepts:
        - ContainerDepartureProposeMsgBody
    """
    t = Template(thread=thread)
    t.set_metadata("performative", "propose")
    t.set_metadata("topic", "container_departure")
    return t


def CONTAINER_DEPARTURE_REJECT_PROPOSAL_TEMPLATE(
    thread: Optional[str] = None,
) -> Template:
    """
    Template for container departure reject proposal message.

    Args:
        thread (str, optional): Thread ID used for accepting only given conversation.

    Accepts:
        - ContainerDepartureRejectProposalMsgBody
    """
    t = Template(thread=thread)
    t.set_metadata("performative", "reject_proposal")
    t.set_metadata("topic", "container_departure")
    return t

def CONTAINER_DEPARTURE_ACCEPT_PROPOSAL_TEMPLATE(
    thread: Optional[str] = None,
) -> Template:
    """ 
    Template for container departure accept proposal message.
    
    Args:
        thread (str, optional): Thread ID used for accepting only given conversation.

    Accepts:
        - ContainerDepartureAcceptProposalMsgBody
    """
    t = Template(thread=thread)
    t.set_metadata("performative", "accept_proposal")
    t.set_metadata("topic", "container_departure")
    return t


class ContainerDepartureCFPMsgBody(MsgBody):
    def __init__(self, container_ids: list[str], date: datetime, transfer_point_id: Optional[int] = None):
        """
        Container departure CFP message body.

        Args:
            container_ids (list[str]): List of container IDs.
            date (datetime): Date of departure.
            transfer_point_id (Optional[int], optional): ID of transfer point. Used only for CFP from transtainer to crane.
        """
        self.container_ids = container_ids
        if isinstance(date, datetime):
            date = date.isoformat()
        self.date = date
        self.transfer_point_id = transfer_point_id

    def create_message(
        self, to: Union[JID, str], reply_by: Union[datetime, str], thread: str
    ) -> Message:
        msg = super().create_message(to, reply_by, thread)
        msg.set_metadata("performative", "cfp")
        msg.set_metadata("topic", "container_departure")
        return msg


class ContainerDepartureRefuseMsgBody(MsgBody):
    def __init__(self):
        """Refusal of container departure CFP."""
        super().__init__()

    def create_message(self, to: Union[JID, str], thread: str) -> Message:
        msg = super().create_message(to, thread=thread)
        msg.set_metadata("performative", "refuse")
        msg.set_metadata("topic", "container_departure")
        return msg


class ContainerDepartureProposeMsgBody(MsgBody):
    def __init__(self, cost: float, container_ids: list[str]):
        """
        Propose for CFP of container departure.

        Args:
            cost (float): Cost of container departure.
            container_ids (list[str]): List of container IDs which can be departed.

        Response:
            - ContainerDepartureRejectProposalMsgBody
            - ContainerDepartureAcceptProposalMsgBody
        """
        self.cost = cost
        self.container_ids = container_ids

    def create_message(
        self, to: Union[JID, str], reply_by: Union[datetime, str], thread: str
    ) -> Message:
        msg = super().create_message(to, reply_by, thread)
        msg.set_metadata("performative", "propose")
        msg.set_metadata("topic", "container_departure")
        return msg


class ContainerDepartureRejectProposalMsgBody(MsgBody):
    def __init__(self):
        """Reject proposal of container departure."""
        super().__init__()

    def create_message(self, to: Union[JID, str], thread: str) -> Message:
        msg = super().create_message(to, thread=thread)
        msg.set_metadata("performative", "reject_proposal")
        msg.set_metadata("topic", "container_departure")
        return msg


class ContainerDepartureAcceptProposalMsgBody(MsgBody):
    def __init__(self):
        """Accept proposal of container departure."""
        super().__init__()

    def create_message(self, to: Union[JID, str], thread: str) -> Message:
        msg = super().create_message(to, thread=thread)
        msg.set_metadata("performative", "accept_proposal")
        msg.set_metadata("topic", "container_departure")
        return msg
