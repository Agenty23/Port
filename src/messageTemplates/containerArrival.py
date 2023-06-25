from messageTemplates.msgBody import MsgBody
from spade.template import Template
from spade.message import Message
from datetime import datetime
from typing import Optional, Union
from aioxmpp import JID


def CONTAINER_ARRIVAL_CFP_TEMPLATE(thread: Optional[str] = None) -> Template:
    """
    Template for container arrival CFP message.

    Args:
        thread (str, optional): Thread ID used for accepting only given conversation.

    Accepts:
        - ContainerArrivalCFPMsgBody
    """
    t = Template(thread=thread)
    t.set_metadata("performative", "cfp")
    t.set_metadata("topic", "container_arrival")
    return t


def CONTAINER_ARRIVAL_REFUSE_TEMPLATE(thread: Optional[str] = None) -> Template:
    """
    Template for container arrival refuse message.

    Args:
        thread (str, optional): Thread ID used for accepting only given conversation.

    Accepts:
        - ContainerArrivalRefuseMsgBody
    """
    t = Template(thread=thread)
    t.set_metadata("performative", "refuse")
    t.set_metadata("topic", "container_arrival")
    return t


def CONTAINER_ARRIVAL_PROPOSE_TEMPLATE(thread: Optional[str] = None) -> Template:
    """
    Template for container arrival propose message.

    Args:
        thread (str, optional): Thread ID used for accepting only given conversation.

    Accepts:
        - ContainerArrivalProposeMsgBody
    """
    t = Template(thread=thread)
    t.set_metadata("performative", "propose")
    t.set_metadata("topic", "container_arrival")
    return t


def CONTAINER_ARRIVAL_REJECT_PROPOSAL_TEMPLATE(
    thread: Optional[str] = None,
) -> Template:
    """
    Template for container arrival reject proposal message.

    Args:
        thread (str, optional): Thread ID used for accepting only given conversation.

    Accepts:
        - ContainerArrivalRejectProposalMsgBody
    """
    t = Template(thread=thread)
    t.set_metadata("performative", "reject-proposal")
    t.set_metadata("topic", "container_arrival")
    return t


def CONTAINER_ARRIVAL_ACCEPT_PROPOSAL_TEMPLATE(
    thread: Optional[str] = None,
) -> Template:
    """
    Template for container arrival accept proposal message.

    Args:
        thread (str, optional): Thread ID used for accepting only given conversation.

    Accepts:
        - ContainerArrivalAcceptProposalMsgBody
    """
    t = Template(thread=thread)
    t.set_metadata("performative", "accept-proposal")
    t.set_metadata("topic", "container_arrival")
    return t


class ContainerArrivalCFPMsgBody(MsgBody):
    def __init__(self, container_ids: list[str], date: datetime):
        """
        Container arrival CFP message body.

        Args:
            container_ids (list[str]): List of arriving container IDs.
            date (datetime): Expected arrival date.

        Response:
            - ContainerArrivalProposeMsgBody
            - ContainerArrivalRefuseMsgBody
        """
        self.container_ids = container_ids
        if isinstance(date, datetime):
            date = date.isoformat()
        self.date = date

    def create_message(self, to: Union[JID, str], reply_by: Union[datetime, str], thread: str) -> Message:
        msg = super().create_message(to, reply_by=reply_by, thread=thread)
        msg.set_metadata("performative", "cfp")
        msg.set_metadata("topic", "container_arrival")
        return msg


class ContainerArrivalRefuseMsgBody(MsgBody):
    def __init__(self):
        """Refusal of container arrival CFP."""
        super().__init__()


    def create_message(self, to: Union[JID, str], thread: str) -> Message:
        msg = super().create_message(to, thread=thread)
        msg.set_metadata("performative", "refuse")
        msg.set_metadata("topic", "container_arrival")
        return msg


class ContainerArrivalProposeMsgBody(MsgBody):
    def __init__(self, cost: float, container_count: int):
        """
        Proposes for CFP of container arrival.

        Args:
            cost (float): Best cost of container arrival.
            container_count (int): Number of containers that can be handled.
        """
        self.cost = cost
        self.container_count = container_count

    def create_message(self, to: Union[JID, str], reply_by: Union[datetime, str],  thread: str) -> Message:
        msg = super().create_message(to, reply_by=reply_by, thread=thread)
        msg.set_metadata("performative", "propose")
        msg.set_metadata("topic", "container_arrival")
        return msg


class ContainerArrivalRejectProposalMsgBody(MsgBody):
    def __init__(self):
        """Rejects proposal of container arrival."""
        super().__init__()

    def create_message(self, to: Union[JID, str], thread: str):
        msg = super().create_message(to, thread=thread)
        msg.set_metadata("performative", "reject-proposal")
        msg.set_metadata("topic", "container_arrival")
        return msg


class ContainerArrivalAcceptProposalMsgBody(MsgBody):
    def __init__(self):
        """Accepts proposal of container arrival."""
        super().__init__()

    def create_message(self, to: Union[JID, str], thread: str):
        msg = super().create_message(to, thread=thread)
        msg.set_metadata("performative", "accept-proposal")
        msg.set_metadata("topic", "container_arrival")
        return msg
