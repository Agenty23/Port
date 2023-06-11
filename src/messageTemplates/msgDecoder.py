from json import JSONDecoder
import messageTemplates.yellowPagesAgentTemplates as ypat

MsgBodyClassess = {
    "portRegistration" : ypat.portRegistration,
    "craneRegistration" : ypat.craneRegistration,
    "transtainerRegistration" : ypat.transtainerRegistration,
    "portListRequest" : ypat.portListRequest,
    "craneListRequest" : ypat.craneListRequest,
    "transtainerListRequest" : ypat.transtainerListRequest
}
    

class MsgDecoder(JSONDecoder):
    def __init__(self):
        JSONDecoder.__init__(self, object_hook=self.dict_to_object)
    
    def dict_to_object(self, d):
        if type(d) is not dict:
            return None

        key = list(d.keys())[0]
        if key in MsgBodyClassess:
            return MsgBodyClassess[key](**d[key])
        return None