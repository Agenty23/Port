from agents.loggingAgent import LoggingAgent
from spade.behaviour import PeriodicBehaviour
from datetime import datetime, timedelta
from messageTemplates.basicTemplates import BLOCK_TEMPLATE

class ThreadCachingAgent(LoggingAgent):
    def __init__(self, jid: str, password: str):
        super().__init__(jid, password)
        self.container_arrival_threads_body = {}
        self.container_arrival_threads_reply_by = {}

    async def setup(self):
        self.add_behaviour(
            self.CleanUpBehav(
                period=120, start_at=datetime.now() + timedelta(seconds=120)
            ),
            template=BLOCK_TEMPLATE,
        )
    
    class CleanUpBehav(PeriodicBehaviour):
        def cleanup(self, reply_by: dict[str, datetime], body: dict[str, object]):
            log = self.agent.log
            for thread, reply_by in reply_by.items():
                if reply_by < datetime.now():
                    log(f"Thread {thread} timed out")
                    try:
                        del body[thread]
                    except KeyError:
                        continue
                    try:
                        del reply_by[thread]
                    except KeyError:
                        continue

        async def run(self):
            log = self.agent.log
            log("Cleaning up...")
            self.cleanup(
                self.agent.container_arrival_threads_body,
                self.agent.container_arrival_threads_reply_by,
            )
