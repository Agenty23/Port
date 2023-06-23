from messageTemplates.msgBody import MsgBody
from spade.template import Template

# region Template for service registration in yellow pages agent
# ----------------------------------------
# Message template: REGISTER_REQUEST
REGISTER_REQUEST_TEMPLATE = Template()
REGISTER_REQUEST_TEMPLATE.set_metadata("performative", "request")
REGISTER_REQUEST_TEMPLATE.set_metadata("topic", "register")


# Message: PortRegistration|CraneRegistration|TranstainerRegistration
class RegistrationMsgBody(MsgBody):
    def create_message(self, to: str):
        msg = super().create_message(to)
        msg.set_metadata("performative", "request")
        msg.set_metadata("topic", "register")
        return msg


class PortRegistrationMsgBody(RegistrationMsgBody):
    def __init__(self, port_jid: str, location: str):
        self.port_jid = port_jid
        self.location = location


class CraneRegistrationMsgBody(RegistrationMsgBody):
    def __init__(
        self,
        crane_jid: str,
        location: str,
        docks_ids: list[int],
        transfer_point_ids: list[int],
    ):
        self.crane_jid = crane_jid
        self.location = location
        self.docks_ids = docks_ids
        self.transfer_point_ids = transfer_point_ids


class TranstainerRegistrationMsgBody(RegistrationMsgBody):
    def __init__(self, transtainer_jid: str, location: str, transfer_point_ids: int):
        self.transtainer_jid = transtainer_jid
        self.location = location
        self.transfer_point_ids = transfer_point_ids


# Response message template
REGISTER_AGREE_TEMPLATE = Template()
REGISTER_AGREE_TEMPLATE.set_metadata("performative", "agree")
REGISTER_AGREE_TEMPLATE.set_metadata("topic", "register")

REGISTER_REFUSE_TEMPLATE = Template()
REGISTER_REFUSE_TEMPLATE.set_metadata("performative", "refuse")
REGISTER_REFUSE_TEMPLATE.set_metadata("topic", "register")


# Response message: RegistrationResponse
class RegistrationAgreeResponseMsgBody(MsgBody):
    def create_message(self, to: str):
        msg = super().create_message(to)
        msg.set_metadata("performative", "agree")
        msg.set_metadata("topic", "register")
        return msg


class RegistrationRefuseResponse(MsgBody):
    def create_message(self, to: str):
        msg = super().create_message(to)
        msg.set_metadata("performative", "refuse")
        msg.set_metadata("topic", "register")
        return msg


# ----------------------------------------
# endregion


# region Templates for service lookup from yellow pages agent
# ----------------------------------------
# Message template: SERVICES_LIST_QUERY
SERVICES_LIST_QUERY_REF_TEMPLATE = Template()
SERVICES_LIST_QUERY_REF_TEMPLATE.set_metadata("performative", "query_ref")
SERVICES_LIST_QUERY_REF_TEMPLATE.set_metadata("topic", "services_list")


# Message: PortListRequest|CraneListRequest|TranstainerListRequest
class ServicesListRequestMsgBody(MsgBody):
    def create_message(self, to: str):
        msg = super().create_message(to)
        msg.set_metadata("performative", "query_ref")
        msg.set_metadata("topic", "services_list")
        return msg


class PortListRequestMsgBody(ServicesListRequestMsgBody):
    def __init__(self, location: str):
        self.location = location


class CraneListRequestMsgBody(ServicesListRequestMsgBody):
    def __init__(self, location: str, dock_id: int):
        self.location = location
        self.dock_id = dock_id


class TranstainerListRequestMsgBody(ServicesListRequestMsgBody):
    def __init__(self, location: str, transfer_point_id: int):
        self.location = location
        self.transfer_point_id = transfer_point_id


# Response message template: SERVICES_LIST_INFORM
SERVICES_LIST_INFORM_TEMPLATE = Template()
SERVICES_LIST_INFORM_TEMPLATE.set_metadata("performative", "inform")
SERVICES_LIST_INFORM_TEMPLATE.set_metadata("topic", "services_list")


# Response message: ServicesListResponse
class ServicesListResponseMsgBody(MsgBody):
    def __init__(self, service_jids: list[str]):
        self.service_jids = service_jids

    def create_message(self, to: str):
        msg = super().create_message(to)
        msg.set_metadata("performative", "inform")
        msg.set_metadata("topic", "services_list")
        return msg


# ----------------------------------------
# endregion
