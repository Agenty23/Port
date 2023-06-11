from json import JSONEncoder

class ObjectEncoder(JSONEncoder):
    def default(self, o):
        result = {}
        result[o.__class__.__name__] = o.__dict__
        return result
    

class MsgBody:
    def toJSON(self):
        return ObjectEncoder().encode(self)