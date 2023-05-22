import time
from operatorAgent import OperatorAgent
from portAgent import PortAgent
from craneAgent import CraneAgent
from transtainerAgent import TranstainerAgent

print("Simulation starting...")

port = PortAgent("port@jabbim.pl", "qwert")
port.start().result()
crane = CraneAgent("test_agent@jabbim.pl/6", "123")
crane.start().result()
transtainer1 = TranstainerAgent("test_agent@jabbim.pl/3", "123")
transtainer2 = TranstainerAgent("test_agent@jabbim.pl/4", "123")
transtainer3 = TranstainerAgent("test_agent@jabbim.pl/5", "123")
transtainer1.start().result()
transtainer1.set_name("Transtainer1")
transtainer1.set_containers({"AS123","ZX234","12345"})
transtainer2.start().result()
transtainer2.set_name("Transtainer2")
transtainer2.set_containers({"aaaaa","bbbbb","ccccc"})
transtainer3.start().result()
transtainer3.set_name("Transtainer3")
transtainer3.set_containers({"11111","22222","33333"})
operator = OperatorAgent("test_agent@jabbim.pl/2", "123")
operator.start().result()


print("Wait until user interrupts with ctrl+C")
while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break
operator.stop()