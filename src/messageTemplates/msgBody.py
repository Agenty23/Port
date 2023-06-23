from json import JSONEncoder
from spade.message import Message


class ObjectEncoder(JSONEncoder):
    def default(self, o):
        result = {}
        result[o.__class__.__name__] = o.__dict__
        return result


class MsgBody:
    def create_message(self, to: str):
        msg = Message(to)
        msg.body = self.toJSON()
        return msg

    def toJSON(self):
        return ObjectEncoder().encode(self)
