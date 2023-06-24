from agents.loggingAgent import LoggingAgent
from spade.message import Message
from spade.behaviour import OneShotBehaviour
from datetime import datetime, timedelta
from spade.message import Message
from spade.template import Template
from messageTemplates.yellowPagesAgentTemplates import (
    PortListRequestMsgBody,
    SERVICES_LIST_INFORM_TEMPLATE,
)
from messageTemplates.msgDecoder import decode_msg
from messageTemplates.containerArrivalTemplates import (
    ContainerArrivalCFPMsgBody,
    CONTAINER_ARRIVAL_PROPOSE_TEMPLATE,
    CONTAINER_ARRIVAL_REFUSE_TEMPLATE,
    ContainerArrivalAcceptProposalMsgBody,
    ContainerArrivalRejectProposalMsgBody,
)
from uuid import uuid4


class OperatorAgent(LoggingAgent):
    def __init__(
        self,
        jid: str,
        password: str,
        action: str,
        container_ids: list[str],
        date: datetime,
        location: str,
        yellow_pages_jid: str,
    ):
        super().__init__(jid, password)
        self.action = action
        self.container_ids = container_ids
        self.date = date
        self.location = location
        self.yellow_pages_jid = yellow_pages_jid

    async def setup(self):
        if self.action == "pickup":
            self.add_behaviour(
                self.RequestContainerBehaviour(),
                template=(
                    SERVICES_LIST_INFORM_TEMPLATE
                    | CONTAINER_ARRIVAL_PROPOSE_TEMPLATE
                    | CONTAINER_ARRIVAL_REFUSE_TEMPLATE
                ),
            )
        elif self.action == "dropoff":
            self.add_behaviour(
                self.RegisterContainerBehaviour(),
                template=(SERVICES_LIST_INFORM_TEMPLATE),
            )
        else:
            raise ValueError("Unknown action")
        self.log("Operator agent started")

    async def get_port_list(self, parent_behaviour, location: str) -> list[str]:
        log = parent_behaviour.agent.log

        port_list_request = PortListRequestMsgBody(location)
        await parent_behaviour.send(
            port_list_request.create_message(self.yellow_pages_jid)
        )

        port_list = await parent_behaviour.receive(timeout=30)
        if port_list is None:
            log("No port available.")
            return None
        
        port_list = decode_msg(port_list).service_jids
        log(f"Port list received: {port_list}")
        return port_list

    class RequestContainerBehaviour(OneShotBehaviour):
        async def run(self):
            log = self.agent.log
            log(f"Requesting pick up of containers (on {self.agent.date}):")
            log(",".join(self.agent.container_ids))

            port_list = await self.agent.get_port_list(self, self.agent.location)
            if port_list is None:
                return
            
            reply_by = datetime.now() + timedelta(seconds=60)
            cfp = ContainerArrivalCFPMsgBody(
                    self.agent.container_ids, self.agent.date
                )
            thread = uuid4().hex
            for port in port_list:
                await self.send(cfp.create_message(port, reply_by, thread))
                log(f"Pickup request sent to port [{port}].")

            log(f"Waiting for responses till {reply_by} ...")
            cost_port_map = {}
            while datetime.now() <= reply_by:
                while (reply := await self.receive(timeout=1)) is not None:
                    if reply.thread != thread:
                        log(f"Unexpected message from {reply.sender}")
                        continue

                    if CONTAINER_ARRIVAL_PROPOSE_TEMPLATE.match(reply):
                        log(f"Container pickup accepted by {reply.sender}")
                        cost_port_map[str(reply.sender)] = decode_msg(reply).cost

                    elif CONTAINER_ARRIVAL_REFUSE_TEMPLATE.match(reply):
                        log(f"Container pickup refused by {reply.sender}")
                    else:
                        log(f"Unexpected message from {reply.sender}")
            
            if len(cost_port_map) == 0:
                log("No port accepted the request.")
                return
            
            min_cost_port = min(cost_port_map, key=cost_port_map.get)
            log(f"Container pickup accepted by {min_cost_port} with cost {cost_port_map[min_cost_port]}")
            await self.send(ContainerArrivalAcceptProposalMsgBody().create_message(min_cost_port, thread))
            for port in cost_port_map:
                if port != min_cost_port:
                    await self.send(ContainerArrivalRejectProposalMsgBody().create_message(port, thread))


        async def on_end(self):
            self.agent.log("Shutting down ...")
            await self.agent.stop()

    class RegisterContainerBehaviour(OneShotBehaviour):
        async def run(self):
            log = self.agent.log
            log(f"Requesting drop off of containers (on {self.agent.date}):")
            log(",".join(self.agent.container_ids))

            portList = await self.agent.get_port_list(self, self.agent.location)

            self.kill(exit_code=0)
