from json import loads
from typing import Optional
from spade.message import Message
from datetime import datetime
from messageTemplates.msgBody import MsgBody
import messageTemplates.agentRegistration as ar
import messageTemplates.servicesListRequest as slr
import messageTemplates.containerArrival as cat

msg_body_classes = {
    "PortRegistrationMsgBody" : ar.PortRegistrationRequestMsgBody,
    "CraneRegistrationRequestMsgBody" : ar.CraneRegistrationRequestMsgBody,
    "TranstainerRegistrationRequestMsgBody" : ar.TranstainerRegistrationRequestMsgBody,
    "RegistrationAgreeMsgBody" : ar.RegistrationAgreeMsgBody,
    "RegistrationRefuseMsgBody" : ar.RegistrationRefuseMsgBody,

    "PortListQueryRefMsgBody" : slr.PortListRequestMsgBody,
    "CraneListQueryRefMsgBody" : slr.CraneListQueryRefMsgBody,
    "TranstainerListQueryRefMsgBody" : slr.TranstainerListQueryRefMsgBody,
    "ServicesListInformMsgBody" : slr.ServicesListInformMsgBody,

    "ContainerArrivalCFPMsgBody" : cat.ContainerArrivalCFPMsgBody,
    "ContainerArrivalRefuseMsgBody" : cat.ContainerArrivalRefuseMsgBody,
    "ContainerArrivalProposeMsgBody" : cat.ContainerArrivalProposeMsgBody,
    "ContainerArrivalRejectProposalMsgBody" : cat.ContainerArrivalRejectProposalMsgBody,
    "ContainerArrivalAcceptProposalMsgBody" : cat.ContainerArrivalAcceptProposalMsgBody,
}

def decode_msg(msg: Message) -> Optional[MsgBody]:
    """
    Decodes a message body into a corresponding object.

    Args:
        msg (spade.message.Message): Message to decode.
    """
    msgBody = loads(msg.body)
    if type(msgBody) is not dict:
        return None

    key = list(msgBody.keys())[0]
    if msgBody[key] is not None and 'date' in msgBody[key] and type(msgBody[key]['date']) is str:
        msgBody[key]['date'] = datetime.fromisoformat(msgBody[key]['date'])
    if key in msg_body_classes:
        return msg_body_classes[key](**msgBody[key])
    
    return None