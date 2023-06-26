from time import sleep
from agents.portAgent import PortAgent
from agents.craneAgent import CraneAgent
from agents.transtainerAgent import TranstainerAgent
from agents.yellowPagesAgent import YellowPagesAgent
import os
import numpy as np
import random as rand
import string
from GUI.operatorGUI import getPortContainerClientInput

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

yellow_pages = YellowPagesAgent(yellow_pages_jid, yellow_pages_password)
yellow_pages.start().result()

port = PortAgent(port_jid, port_password, "Gdansk", yellow_pages_jid)
port.start()

crane = CraneAgent(
    crane_base_jid + "/1",
    crane_password,
    "Gdansk",
    [1, 2],
    [1, 2, 3, 4],
    yellow_pages_jid,
)
crane.start()

container_ids_pool = [
    "".join(rand.choices(string.ascii_letters + string.digits, k=5))
    for i in range(3 * 3 * 3 * num_of_transtainers)
]
container_ids_taken = list()

trainstainers = []
for i in range(num_of_transtainers):
    yard = np.ndarray((3, 3, 3), dtype=object)
    yard.fill("")
    for x in range(3):
        for y in range(3):
            for z in range(3):
                if rand.random() > 0.5:
                    yard[x][y][z] = container_ids_pool.pop(
                        rand.randint(0, len(container_ids_pool) - 1)
                    )
                    container_ids_taken.append(yard[x][y][z])
                else:
                    break
    print(yard)

    trainstainers.append(
        TranstainerAgent(
            transtainer_base_jid + "/" + str(i),
            transtainer_password,
            "Gdansk",
            i + 1,
            yellow_pages_jid,
            yard,
        )
    )
    trainstainers[i].start().result()

try:
    sleep(5)

    getPortContainerClientInput(operator_base_jid, operator_password, yellow_pages_jid)

except KeyboardInterrupt:
    print("Simulation stopped")
    port.stop()
    crane.stop()
    for transtainer in trainstainers:
        transtainer.stop()
    yellow_pages.stop()