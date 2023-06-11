import time
from agents.operatorAgent import OperatorAgent
from agents.portAgent import PortAgent
from agents.craneAgent import CraneAgent
from agents.transtainerAgent import TranstainerAgent
from agents.yellowPagesAgent import YellowPagesAgent
import os

print("Simulation starting...")
print("Can be stopped with ctrl+C")

############## CONFIG ##############
yellow_pages_jid = os.environ.get("YELLOW_PAGES_JID")
yellow_pages_password = os.environ.get("YELLOW_PAGES_PASSWORD")
port_jid = os.environ.get("PORT_JID")
port_password = os.environ.get("PORT_PASSWORD")
transtainer_base_jid = os.environ.get("TRANSTAINER_BASE_JID")
transtainer_password = os.environ.get("TRANSTAINER_PASSWORD")
crane_base_jid = os.environ.get("CRANE_BASE_JID")
crane_password = os.environ.get("CRANE_PASSWORD")
operator_base_jid = os.environ.get("OPERATOR_BASE_JID")
operator_password = os.environ.get("OPERATOR_PASSWORD")

num_of_transtainers = 3

############ END CONFIG ############

port = PortAgent(port_jid, port_password)
port.start().result()

crane = CraneAgent(crane_base_jid + "/1", crane_password, port.jid)
crane.start().result()

trainstainers = []
for i in range(num_of_transtainers):
    trainstainers.append(TranstainerAgent(transtainer_base_jid + "/" + str(i), transtainer_password, port.jid, crane.jid))
    trainstainers[i].start().result()
     
trainstainers[0].set_containers({"AS123","ZX234","12345"})
trainstainers[1].set_containers({"aaaaa","bbbbb","ccccc"})
trainstainers[2].set_containers({"11111","22222","33333"})

operator = OperatorAgent(operator_base_jid + "/1", operator_password, "pickup", port.jid)
operator.start().result()

while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break
operator.stop()