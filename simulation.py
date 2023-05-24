import time
from operatorAgent import OperatorAgent
from portAgent import PortAgent
from craneAgent import CraneAgent
from transtainerAgent import TranstainerAgent
import os

print("Simulation starting...")

port_jid = os.environ.get("PORT_JID")
port_password = os.environ.get("PORT_PASSWORD")

transtainer_base_jid = os.environ.get("TRANSTAINER_BASE_JID")
transtainer_password = os.environ.get("TRANSTAINER_PASSWORD")

crane_base_jid = os.environ.get("CRANE_BASE_JID")
crane_password = os.environ.get("CRANE_PASSWORD")

operator_base_jid = os.environ.get("OPERATOR_BASE_JID")
operator_password = os.environ.get("OPERATOR_PASSWORD")

port = PortAgent(port_jid, port_password)
port.start().result()
port.set_name("Port")
crane = CraneAgent(crane_base_jid + "/1", crane_password, port.jid)
crane.start().result()
crane.set_name("Crane")
transtainer1 = TranstainerAgent(transtainer_base_jid + "/1", transtainer_password, port.jid, crane.jid)
transtainer2 = TranstainerAgent(transtainer_base_jid + "/2", transtainer_password, port.jid, crane.jid)
transtainer3 = TranstainerAgent(transtainer_base_jid + "/3", transtainer_password, port.jid, crane.jid)
transtainer1.start().result()
transtainer1.set_name("Transtainer1")
transtainer1.set_containers({"AS123","ZX234","12345"})
transtainer2.start().result()
transtainer2.set_name("Transtainer2")
transtainer2.set_containers({"aaaaa","bbbbb","ccccc"})
transtainer3.start().result()
transtainer3.set_name("Transtainer3")
transtainer3.set_containers({"11111","22222","33333"})
operator = OperatorAgent(operator_base_jid + "/1", operator_password, "pickup", port.jid)
operator.start().result()


print("Wait until user interrupts with ctrl+C")
while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break
operator.stop()