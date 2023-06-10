# Port

For sake of simplicity we decided on unified port layout. Each port has its own, unique location, and set of docks (such as a wharf of platform), where one ship can be morred to exactly one dock at a time. Docks can be served by multiple cranes. Those cranes have also access to multiple transfer points at yard, where each transfer point has exactly one transtainer assigned. Each transtainer has its own year. Ports may cooperate with different operators, interchangeably. Therefore we need the following mapping between agents and physical entities:

| Agent | Physical entity | Relation |
| --- | --- | --- |
| Port | Location | One-to-One |
| Port | Dock | One-to-Many |
| Crane | Dock | Many-to-Many |
| Crane | Transfer point | Many-to-Many |
| Transtainer | Transfer point | One-to-One |

This also leads to relations between agents:

| Agent 1 | Agent 2 | Relation |
| --- | --- | --- |
| Port | Crane | One-to-Many |
| Crane | Transtainer | Many-to-Many |
| Transtainer | Container | One-to-Many |
