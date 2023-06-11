from json import JSONEncoder, JSONDecoder
import messageTemplates.yellowPagesAgentTemplates as ypat

class ObjectEncoder(JSONEncoder):
    def default(self, o):
        result = {}
        result[o.__class__.__name__] = o.__dict__
        return result
    

MsgBodyClassess = {
    "portRegistration" : ypat.portRegistration,
    "craneRegistration" : ypat.craneRegistration,
    "transtainerRegistration" : ypat.transtainerRegistration,
    "portListRequest" : ypat.portListRequest,
    "craneListRequest" : ypat.craneListRequest,
    "transtainerListRequest" : ypat.transtainerListRequest
}
    

class ObjectDecoder(JSONDecoder):
    def __init__(self):
        JSONDecoder.__init__(self, object_hook=self.dict_to_object)
    
    def dict_to_object(self, d):
        if type(d) is not dict:
            return None

        key = list(d.keys())[0]
        if key in MsgBodyClassess:
            return MsgBodyClassess[key](**d[key])
        return None
    

class MsgBody:
    def toJSON(self):
        return ObjectEncoder().encode(self)
    
    @staticmethod
    def fromJSON(jsonStr):
        return ObjectDecoder().decode(jsonStr)