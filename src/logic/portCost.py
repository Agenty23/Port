from datetime import datetime
from random import normalvariate, sample

def calculatePortCost(date: datetime, crane_proposals: dict[str, {float, int}]) -> tuple[float, list[str]]:
    """@return [total_cost, [crane_ids]]"""
    crane = sample(crane_proposals.keys(), 1)
    return normalvariate(50, 50), crane_proposals[crane[0]].container_count, crane