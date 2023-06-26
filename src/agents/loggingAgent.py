from spade.agent import Agent
from datetime import datetime


class LoggingAgent(Agent):
    def log(self, message: str) -> None:
        """
        Prints on the console a message with the agent's JID and a timestamp.

        Args:
            message (str): Message to be printed.
        """
        agent_stamp = f"[{str(self.jid)}]"
        timestamp = f"<{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}>"
        print(f"{agent_stamp : <30}{message : ^100}{timestamp : <22}")
