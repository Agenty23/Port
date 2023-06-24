from json import loads
from spade.message import Message
import messageTemplates.yellowPagesAgentTemplates as ypat

msg_body_classes = {
    "PortRegistrationMsgBody" : ypat.PortRegistrationMsgBody,
    "CraneRegistrationMsgBody" : ypat.CraneRegistrationMsgBody,
    "TranstainerRegistrationMsgBody" : ypat.TranstainerRegistrationMsgBody,
    "PortListRequestMsgBody" : ypat.PortListRequestMsgBody,
    "CraneListRequestMsgBody" : ypat.CraneListRequestMsgBody,
    "TranstainerListRequestMsgBody" : ypat.TranstainerListRequestMsgBody,
    "ServicesListResponseMsgBody" : ypat.ServicesListResponseMsgBody,
    "RegistrationAgreeResponseMsgBody" : ypat.RegistrationAgreeResponseMsgBody,
    "RegistrationRefuseResponseMsgBody" : ypat.RegistrationRefuseResponseMsgBody,
}

def decode_msg(msg: Message) -> object:
    msgBody = loads(msg.body)
    if type(msgBody) is not dict:
        return None

    key = list(msgBody.keys())[0]
    if key in msg_body_classes:
        return msg_body_classes[key](**msgBody[key])
    return None