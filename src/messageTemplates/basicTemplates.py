from messageTemplates.msgBody import MsgBody
from spade.template import Template

# region Template for not understood messages
# ----------------------------------------
# Message template: NOT_UNDERSTOOD
NOT_UNDERSTOOD = Template()
NOT_UNDERSTOOD.set_metadata("performative", "not-understood")

# Message: NotUnderstood
class NotUnderstoodMsgBody(MsgBody):
    def create_message(self, to: str):
        msg = super().create_message(to)
        msg.set_metadata("performative", "not-understood")
        return msg


# endregion