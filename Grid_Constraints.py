

class GridConstraint:
    """
    A class representing a constraint on the grid for a single agent.

    Attributes:
    -----------
    agent_id : int
        The ID of the agent that this constraint applies to.
    vertex : bool
        A boolean indicating whether the constraint is satisfied.
    edge : float
        The value of the constraint.
    timestep_ : int
        The timestep at which the constraint applies.
    """

    def __init__(self) -> None:
        self.agent_id: int = None
        self.vertex: bool = False
        self.edge: float = None
        self.timestep_: int = None

    def __repr__(self) -> str:
        return f"{self.agent_id}"
