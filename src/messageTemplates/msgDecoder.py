from json import loads
from spade.message import Message
from datetime import datetime
import messageTemplates.basicTemplates as bt
import messageTemplates.yellowPagesAgentTemplates as ypat
import messageTemplates.containerArrivalTemplates as cat

msg_body_classes = {
    "NotUnderstoodMsgBody" : bt.NotUnderstoodMsgBody,
    "PortRegistrationMsgBody" : ypat.PortRegistrationMsgBody,
    "CraneRegistrationMsgBody" : ypat.CraneRegistrationMsgBody,
    "TranstainerRegistrationMsgBody" : ypat.TranstainerRegistrationMsgBody,
    "PortListRequestMsgBody" : ypat.PortListRequestMsgBody,
    "CraneListRequestMsgBody" : ypat.CraneListRequestMsgBody,
    "TranstainerListRequestMsgBody" : ypat.TranstainerListRequestMsgBody,
    "ServicesListResponseMsgBody" : ypat.ServicesListResponseMsgBody,
    "RegistrationAgreeResponseMsgBody" : ypat.RegistrationAgreeResponseMsgBody,
    "RegistrationRefuseResponseMsgBody" : ypat.RegistrationRefuseResponseMsgBody,
    "ContainerArrivalCFPMsgBody" : cat.ContainerArrivalCFPMsgBody,
    "ContainerArrivalRefuseMsgBody" : cat.ContainerArrivalRefuseMsgBody,
    "ContainerArrivalProposeMsgBody" : cat.ContainerArrivalProposeMsgBody,
    "ContainerArrivalRejectProposalMsgBody" : cat.ContainerArrivalRejectProposalMsgBody,
    "ContainerArrivalAcceptProposalMsgBody" : cat.ContainerArrivalAcceptProposalMsgBody,
}

def decode_msg(msg: Message) -> object:
    msgBody = loads(msg.body)
    if type(msgBody) is not dict:
        return None

    key = list(msgBody.keys())[0]
    if msgBody[key] is not None and 'date' in msgBody[key] and type(msgBody[key]['date']) is str:
        msgBody[key]['date'] = datetime.fromisoformat(msgBody[key]['date'])
    if key in msg_body_classes:
        return msg_body_classes[key](**msgBody[key])
    return None