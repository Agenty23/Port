from datetime import datetime
from random import normalvariate, sample

def calculateCraneCost(date: datetime, transtainer_proposals: dict[str, {float, int}]) -> tuple[float, list[str]]:
    """@return [total_cost, [transtainer_ids]]"""
    return [normalvariate(50, 50), sample(transtainer_proposals.keys(), 1)]