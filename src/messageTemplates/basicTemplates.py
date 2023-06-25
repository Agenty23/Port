from spade.template import Template

# Template for blocking every message
def BLOCK_TEMPLATE() -> Template:
    """
    Template for blocking every message
    """
    t = Template(to="blocking", from_="blocking", body="blocking")
    t.set_metadata("blocking", "blocking")
    return t