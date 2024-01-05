from typing import Dict, List, Tuple
from collections import deque

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
        self.path_table: Dict[Tuple[int, int], List[GridConstraint | None]] = {}

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
                self.path_table[position.location()] = []

            if len(self.path_table[position.location()]) <= timestep:
                difference = timestep - len(self.path_table[position.location()]) + 1
                self.path_table[position.location()].extend([None] * difference)

            assert self.path_table[position.location()][timestep] is None

            constraint = GridConstraint()
            constraint.agent_id = agent_id
            constraint.vertex = True
            constraint.edge = position.theta
            constraint.timestep_ = timestep

            self.path_table[position.location()][timestep] = constraint

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
        for constraint in self.path_table[position.location()]:
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

    def delete_entry(self, position: Position, agent_id: int, timestep: int):
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
        constraints = self.path_table.get(position.location())

        if constraints is None:
            return

        constraint = constraints[timestep]

        if constraint is not None:
            assert constraint.agent_id == agent_id
            self.path_table[position.location()][timestep] = None

class OnlineSchedule:
    """
    A class that represents a schedule table for agents.
    Using a priority queue with arrival timestep as priority.

    Attributes:
    -----------
    path_table : Dict[Tuple[int, int], Queue[GridConstraint]]
        A dictionary that maps a tuple of (x, y) coordinates to a
        queue of GridConstraint objects describing the order agents pass through the location.
    """
    def __init__(self, num_agents: int) -> None:
        """
        Initializes a new instance of the ScheduleTable class.

        Parameters:
        -----------
        num_agents: The maximum number of active agents
        """
        self.path_table: Dict[Tuple[int, int], deque[GridConstraint]] = {}
        self.num_agents = num_agents

    def update_plan(self, extension: List[Tuple[Position, int]], agent_id: int):
        """
        Extends or create a path in the schedule table, enforcing the order??.

        Parameters:
        -----------
        agent_id : int
            The ID of the agent.
        path : List[Position]
            A list of positions that the agent will visit.
        """
        for position, timestep in extension:
            if position not in self.path_table:
                self.path_table[position.location()] = deque()
            constraint = GridConstraint()
            constraint.agent_id = agent_id
            constraint.vertex = True
            constraint.edge = position.theta
            constraint.timestep_ = timestep

            self.path_table[position.location()].append(constraint)


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

        Requires:
        ---------
        The agent only checks if it is scheduled enxt along a path that has been inserted into the schedule.
        """
        schedule = self.path_table.get(position.location())
        if not schedule:
            raise ValueError("Position has no schedules at all, not planned to be traversed")
        # Unpleasant internal attribute access because Queue does not provide a peek method.
        # Cannot remove the scheduled action until the action is completed,
        # otherwise we do not properly prevent collisions
        if schedule[0].agent_id == agent_id:
            return True
        return False

    def delete_entry(self, position: Position, agent_id: int, timestep: int):
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
        constraints = self.path_table.get(position.location())

        if constraints is None or not constraints:
            return

        constraint = constraints.popleft()

        if constraint is not None:
            assert constraint.agent_id == agent_id, \
                                 f"Trying to delete {agent_id} on constraint for {constraint.agent_id}"
            assert constraint.timestep_ == timestep

    def remove_path(
        self, agent_id: int, path: List[Tuple[int, Position]]) -> None:
        """
        Removes a path segment from the schedule table.

        Parameters:
        -----------
        agent_id : int
            The ID of the agent.
        path : List[Tuple[int, Position]]
            The list of positions the agent has visited since the last update of its location,
            with the planned timesteps it has completed
        """
        ## Want to also start from the last confirmed timestep
        for timestep, position in path:
            print( "Deleted this, ", self.delete_entry(position, agent_id, timestep))
