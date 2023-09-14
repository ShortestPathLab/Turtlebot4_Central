
class GridConstraint:
    def __init__(self) -> None:
        self.agent_id: int = None
        self.v_: bool = False
        self.e_: float = None
        self.timestep_: int = None

    def __repr__(self) -> str:
        return f"{self.agent_id}"






