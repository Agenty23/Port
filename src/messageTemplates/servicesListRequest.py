from messageTemplates.msgBody import MsgBody
from spade.template import Template
from spade.message import Message
from typing import Optional, Union
from aioxmpp import JID


def SERVICES_LIST_QUERY_REF_TEMPLATE() -> Template:
    """
    Template for services list query to yellow pages agent.

    Accepts:
        - PortListRequestMsgBody
        - CraneListRequestMsgBody
        - TranstainerListRequestMsgBody
    """
    t = Template()
    t.set_metadata("performative", "query_ref")
    t.set_metadata("topic", "services_list")
    return t


def SERVICES_LIST_INFORM_TEMPLATE() -> Template:
    """
    Response message template for services list query from yellow pages agent.

    Accepts:
        - ServicesListResponseMsgBody
    """
    t = Template()
    t.set_metadata("performative", "inform")
    t.set_metadata("topic", "services_list")
    return t


class ServicesListQueryRefMsgBody(MsgBody):
    def create_message(self, to: Union[JID, str]) -> Message:
        msg = super().create_message(to)
        msg.set_metadata("performative", "query_ref")
        msg.set_metadata("topic", "services_list")
        return msg


class PortListQueryRefMsgBody(ServicesListQueryRefMsgBody):
    def __init__(self, location: str) -> None:
        """
        Request for ports list from yellow pages agent.

        Args:
            location (str): Port location.

        Response:
            - ServicesListResponseMsgBody
        """
        self.location = location


class CraneListQueryRefMsgBody(ServicesListQueryRefMsgBody):
    def __init__(
        self,
        location: str,
        dock_ids: Optional[list[int]] = None,
        transfer_point_ids: Optional[list[int]] = None,
    ) -> None:
        """
        Request for cranes list from yellow pages agent.

        Args:
            location (str): Crane location.
            dock_ids (list[int], optional): List of dock IDs served by crane (at least one match required).
            transfer_point_ids (list[int], optional): List of transfer point IDs served by crane (at least one match required).

        Response:
            - ServicesListResponseMsgBody
        """
        self.location = location
        self.dock_ids = dock_ids
        self.transfer_point_ids = transfer_point_ids


class TranstainerListQueryRefMsgBody(ServicesListQueryRefMsgBody):
    def __init__(self, location: str, transfer_point_ids: Optional[list[int]] = None) -> None:
        """
        Request for transtainers list from yellow pages agent.

        Args:
            location (str): Transtainer location.
            transfer_point_ids (list[int], optional): List of transfer point IDs served by transtainer (at least one match required).

        Response:
            - ServicesListResponseMsgBody
        """
        self.location = location
        self.transfer_point_ids = transfer_point_ids


class ServicesListInformMsgBody(MsgBody):
    def __init__(self, service_jids: list[str]) -> None:
        """
        Response for services list query from yellow pages agent.

        Args:
            service_jids (list[str]): List of services JIDs.
        """
        self.service_jids = service_jids

    def create_message(self, to: Union[JID, str]) -> Message:
        msg = super().create_message(to)
        msg.set_metadata("performative", "inform")
        msg.set_metadata("topic", "services_list")
        return msg
