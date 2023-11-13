from typing import Dict, List

from Grid_Constraints import GridConstraint
from Position import Position


class ScheduleTable:
    """
    A class that represents a schedule table for agents.

    Attributes:
    -----------
    path_table : Dict[Tuple[int, int], List[GridConstraint]]
        A dictionary that maps a tuple of (x, y) coordinates to a
        list of GridConstraint objects.
    """

    def __init__(self, agent_plans: Dict[int, List[Position]]) -> None:
        """
        Initializes a new instance of the ScheduleTable class.

        Parameters:
        -----------
        agent_plans : Dict[int, List[Position]]
            A dictionary that maps an agent ID to a list of positions
            that the agent will visit.
        """
        self.path_table: Dict[Position, List[GridConstraint | None]] = {}

        for agent_id, agent_plan in agent_plans.items():
            self.add_path(agent_id, agent_plan)

    def add_path(self, agent_id: int, path: List[Position]) -> None:
        """
        Adds a path to the schedule table.

        Parameters:
        -----------
        agent_id : int
            The ID of the agent.
        path : List[Position]
            A list of positions that the agent will visit.
        """
        for timestep, position in enumerate(path):
            if position not in self.path_table:
                self.path_table[position] = []

            if len(self.path_table[position]) <= timestep:
                difference = timestep - len(self.path_table[position]) + 1
                self.path_table[position].extend([None] * difference)

            assert self.path_table[position][timestep] is None

            constraint = GridConstraint()
            constraint.agent_id = agent_id
            constraint.vertex = True
            constraint.edge = position.theta
            constraint.timestep_ = timestep

            self.path_table[position][timestep] = constraint

    def scheduled(self, position: Position, agent_id: int) -> bool:
        """
        Checks if a position is scheduled for a given agent.

        Parameters:
        -----------
        position : Position
            The position to check.
        agent_id : int
            The ID of the agent.

        Returns:
        --------
        bool
            True if the position is scheduled for the given agent,
            False otherwise.
        """
        for constraint in self.path_table[position]:
            if constraint is None:
                continue
            return constraint.agent_id == agent_id
        return False

    def remove_path(
        self, agent_id: int, path: List[Position], max_timestep: int
    ) -> None:
        """
        Removes a path from the schedule table.

        Parameters:
        -----------
        agent_id : int
            The ID of the agent.
        path : List[Position]
            A list of positions that the agent will visit.
        max_timestep : int
            The maximum timestep to remove the path up to.
        """
        for timestep, position in enumerate(path):
            if timestep >= max_timestep:
                break
            self.delete_entry(position, agent_id, timestep)

    def delete_entry(self, position: Position, agent_id: int, timestep: int) -> None:
        """
        Deletes an entry from the schedule table.

        Parameters:
        -----------
        position : Position
            The position to delete.
        agent_id : int
            The ID of the agent.
        timestep : int
            The timestep of the entry to delete.
        """
        constraints = self.path_table.get(position)

        if constraints is None:
            return

        constraint = constraints[timestep]

        if constraint is not None:
            assert constraint.agent_id == agent_id
            self.path_table[position][timestep] = None
