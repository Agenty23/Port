from json import JSONEncoder
from aioxmpp import JID
from spade.message import Message
from typing import Optional, Union
from datetime import datetime


class ObjectEncoder(JSONEncoder):
    def default(self, o):
        result = {}
        result[o.__class__.__name__] = o.__dict__
        return result


class MsgBody:
    def create_message(self, to: Union[JID, str], reply_by: Optional[Union[datetime, str]] = None, thread: Optional[str] = None) -> Message:
        """
        Creates a message with this object as a encoded to JSON body.

        Args:
            to (JID | str): Receiver of the message.
            reply_by (datetime | str, optional): Deadline for reply.
            thread (str, optional): Thread ID used for conversation tracking.
        """
        if isinstance(to, JID):
            to = str(to)

        msg = Message(to, thread=thread)
        if reply_by is not None:
            if isinstance(reply_by, datetime):
                reply_by = reply_by.isoformat()
            msg.set_metadata("reply-by", reply_by)

        msg.body = ObjectEncoder().encode(self)
        return msg
