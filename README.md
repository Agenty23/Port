# Port
Container Ports are very sophisticated, almost living organisms that are constantly mov- ing and changing. With the staggering amount of cargo that goes through each port and restricted, usually really small area to move and store every single container, proper man- agement system has to be implemented to ensure maximal efficiency as well as security of operations.
In our case, we decided to optimize the storage area of the port. Every single container going in and going out of the port will be processed through our ”hands” and later sent out either by truck, train or ship.
The problem would be non-existent if it was not for the limited space in the port area. Assuming we could prepare infinite amount of slots for containers and later just pick them whenever we need, software of this kind would be unnecessary. Unfortunately, containers have to be stored in stacks, in LIFO system (last in - first out), meaning, that we can only store a container on top of a container that either leaves at the same time, or later. Of course, we will be able to move containers out of the way if necessary, but the aim is to minimize the number of moves.
Additional challenge comes when we add another factor to the equation, which is unpre- dictability of the ”outside world”. While, of course, every transport is meticulously sched- uled, during planning process we cannot take into account e.x weather, road collisions or even thefts. System has to plan everything according to schedule, but also be able to react in case of any differences in real life
Our solution has to be easily implemented into any port. Whether it’s Gdan ́sk, New York or Saint Kitts and Nevis, the principle is the same and given that, our system should be easily scaled to small local port as well as the biggest and most complicated ports around the world. This is why our approach includes Agent Systems. Software based on such approach is easily scalable when implemented correctly. Of course, each time the software would have to be correctly adjusted to the specific situation, but it would only require minor tweaks, not writing it once again from the ground up.
Agent Systems approach will also let us use significantly less computing power in one place, which is really important in environments, where the hardware is already installed and may limit software in terms of processing data. In case of ports, many different stations may have different setups in terms of hardware, so only well written software can handle all the challenges that come with such situations.

## Documentation:

- [ACL as standard for communication](docs/ACL.md)
- [Our port model](docs/Port.md)

## Code structure

- '/src/agents/' - contains all agents definitions with their behaviours but without business logic (how to count the cost of the operation).
- '/src/messageTemplates/' - contains all message templates used in the project. Place where one can find how to prepare message to specific agent.
