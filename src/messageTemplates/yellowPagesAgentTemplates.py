from messageTemplates.msgBody import MsgBody
from spade.template import Template

# region Template for service registration in yellow pages agent
# ----------------------------------------
# Message template
REGISTER_REQUEST = Template()
REGISTER_REQUEST.set_metadata("performative", "request")
REGISTER_REQUEST.set_metadata("topic", "register")

# Message content: portRegistration|craneRegistration|transtainerRegistration
class portRegistration(MsgBody):
    def __init__(self, portJid: str, location: str):
        self.portJid = portJid
        self.location = location

class craneRegistration(MsgBody):
    def __init__(self, craneJid: str, location: str, dockIds: list[int], transferPointIds: list[int]):
        self.craneJid = craneJid
        self.location = location
        self.dockIds = dockIds
        self.transferPointIds = transferPointIds

class transtainerRegistration(MsgBody):
    def __init__(self, transtainerJid: str, location: str, transferPointId: int):
        self.transtainerJid = transtainerJid
        self.location = location
        self.transferPointId = transferPointId

# Response message template
REGISTER_AGREE = Template()
REGISTER_AGREE.set_metadata("performative", "agree")
REGISTER_AGREE.set_metadata("topic", "register")

REGISTER_REFUSE = Template()
REGISTER_REFUSE.set_metadata("performative", "refuse")
REGISTER_REFUSE.set_metadata("topic", "register")

# Response message content: None
# ----------------------------------------
# endregion


# region Templates for service lookup from yellow pages agent
# ----------------------------------------
# Message template
SERVICES_LIST_QUERY_REF = Template()
SERVICES_LIST_QUERY_REF.set_metadata("performative", "query_ref")
SERVICES_LIST_QUERY_REF.set_metadata("topic", "services_list")

# Message content: portListRequest|craneListRequest|transtainerListRequest
class portListRequest:
    def __init__(self, location: str):
        self.location = location

class craneListRequest:
    def __init__(self, location: str, dockId: int):
        self.location = location
        self.dockId = dockId

class transtainerListRequest:
    def __init__(self, location: str, transferPointId: int):
        self.location = location
        self.transferPointId = transferPointId

# Response message template
SERVICES_LIST_INFORM = Template()
SERVICES_LIST_INFORM.set_metadata("performative", "inform")
SERVICES_LIST_INFORM.set_metadata("topic", "services_list")

# Response message content: list[serviceJids : str]
# ----------------------------------------
# endregion