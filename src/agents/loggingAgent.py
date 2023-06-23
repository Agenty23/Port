from spade.agent import Agent
from datetime import datetime


class LoggingAgent(Agent):
    def log(self, message):
        agent_stamp = f"[{str(self.jid)}]"
        timestamp = f"<{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}>"
        print(f"{agent_stamp : <30}{message : ^100}{timestamp : <22}")
