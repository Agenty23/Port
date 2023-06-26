from datetime import datetime
from random import normalvariate

def calculateTranstainerArrivalCost(transtainerAgent, date: datetime, container_count: int) -> tuple[float, dict[str, tuple[int, int, int]]]:
    """@return [total_cost, {container_id: position on yard}]"""
    return normalvariate(50, 50), {"container_id": (0, 0, 0)}

def rearrangeYard(transtainerAgent, containers_placement: dict[str, tuple[int, int, int]]) -> None:
    """Rearrange yard according to the placement of new containers."""
    for container_id, position in containers_placement.items():
        transtainerAgent.yard[position[0]][position[1]][position[2]] = container_id

def calculateTranstainerDepartureCost(transtainerAgent, date: datetime, container_ids: list[str], crane_proposals: dict[str, ]) -> float:
    return normalvariate(50, 50)
    