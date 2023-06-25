from datetime import datetime
from random import normalvariate, sample

def calculatePortCost(date: datetime, crane_proposals: dict[str, {float, int}]) -> tuple[float, list[str]]:
    """@return [total_cost, [crane_ids]]"""
    return [normalvariate(50, 50), sample(crane_proposals.keys(), 1)]