from messageTemplates.msgBody import MsgBody
from spade.template import Template
from spade.message import Message
from typing import Union
from aioxmpp import JID


def REGISTER_REQUEST_TEMPLATE():
    """
    Template for service registration in yellow pages agent.

    Accepts:
        - PortRegistrationMsgBody
        - CraneRegistrationMsgBody
        - TranstainerRegistrationMsgBody
    """
    t = Template()
    t.set_metadata("performative", "request")
    t.set_metadata("topic", "register")
    return t


def REGISTER_AGREE_TEMPLATE():
    """
    Response message template for registration in yellow pages agent.

    Accepts:
        - RegistrationAgreeResponseMsgBody
    """
    t = Template()
    t.set_metadata("performative", "agree")
    t.set_metadata("topic", "register")
    return t


def REGISTER_REFUSE_TEMPLATE():
    """
    Response message template for registration in yellow pages agent.

    Accepts:
        - RegistrationRefuseResponseMsgBody
    """
    t = Template()
    t.set_metadata("performative", "refuse")
    t.set_metadata("topic", "register")
    return t


class RegistrationRequestMsgBody(MsgBody):
    def create_message(self, to: Union[JID, str]) -> Message:
        msg = super().create_message(to)
        msg.set_metadata("performative", "request")
        msg.set_metadata("topic", "register")
        return msg


class PortRegistrationRequestMsgBody(RegistrationRequestMsgBody):
    def __init__(self, port_jid: str, location: str):
        """
        Request for port registration in yellow pages agent.

        Args:
            port_jid (str): Port agent's JID.
            location (str): Port agent's location.

        Response:
            - RegistrationAgreeResponseMsgBody
            - RegistrationRefuseResponseMsgBody
        """
        self.port_jid = port_jid
        self.location = location


class CraneRegistrationRequestMsgBody(RegistrationRequestMsgBody):
    def __init__(
        self,
        crane_jid: str,
        location: str,
        dock_ids: list[int],
        transfer_point_ids: list[int],
    ):
        """
        Request for crane registration in yellow pages agent.

        Args:
            crane_jid (str): Crane agent's JID.
            location (str): Crane agent's location.
            dock_ids (list[int]): List of docks IDs that crane can serve.
            transfer_point_ids (list[int]): List of transfer points IDs that crane can serve.

        Response:
            - RegistrationAgreeResponseMsgBody
            - RegistrationRefuseResponseMsgBody
        """
        self.crane_jid = crane_jid
        self.location = location
        self.dock_ids = dock_ids
        self.transfer_point_ids = transfer_point_ids


class TranstainerRegistrationRequestMsgBody(RegistrationRequestMsgBody):
    def __init__(self, transtainer_jid: str, location: str, transfer_point_id: int):
        """
        Request for transtainer registration in yellow pages agent.

        Args:
            transtainer_jid (str): Transtainer agent's JID.
            location (str): Transtainer agent's location.
            transfer_point_id (int): Transfer point ID that transtainer can serve.

        Response:
            - RegistrationAgreeResponseMsgBody
            - RegistrationRefuseResponseMsgBody
        """
        self.transtainer_jid = transtainer_jid
        self.location = location
        self.transfer_point_id = transfer_point_id


class RegistrationAgreeMsgBody(MsgBody):
    def __init__(self):
        """
        Response on successful registration in yellow pages agent.
        """
        super().__init__()

    def create_message(self, to: Union[JID, str]):
        msg = super().create_message(to)
        msg.set_metadata("performative", "agree")
        msg.set_metadata("topic", "register")
        return msg


class RegistrationRefuseMsgBody(MsgBody):
    def __init__(self):
        """
        Response on failed/refused registration in yellow pages agent.
        """
        super().__init__()

    def create_message(self, to: Union[JID, str]):
        msg = super().create_message(to)
        msg.set_metadata("performative", "refuse")
        msg.set_metadata("topic", "register")
        return msg
