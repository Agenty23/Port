from datetime import datetime
from random import normalvariate, sample

def calculatePortArrivalCost(date: datetime, crane_proposals: dict[str, {float, int}]) -> tuple[float, list[str]]:
    crane = sample(crane_proposals.keys(), 1)
    return normalvariate(50, 50), crane_proposals[crane[0]].container_count, crane

def calculatePortDepartureCost(date: datetime, transtainer_proposals: dict[str, {float, list[str]}]) -> float:
    return normalvariate(50, 50)