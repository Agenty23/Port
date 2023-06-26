from datetime import datetime
from random import normalvariate, sample

def calculateCraneCost(date: datetime, transtainer_proposals: dict[str, {float, int}]) -> tuple[float, int, list[str]]:
    """@return [total_cost, [transtainer_ids]]"""
    transtainer = sample(transtainer_proposals.keys(), 1)
    return normalvariate(50, 50), transtainer_proposals[transtainer[0]].container_count, transtainer