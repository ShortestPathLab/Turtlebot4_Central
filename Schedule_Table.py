from typing import Dict, List, Tuple
from collections import deque, UserDict

from Grid_Constraints import GridConstraint
from Position import Position

class PathReservation(UserDict):
    """A custom dict override to insert Position(x,y,theta) with keys being equal if x and y are equal"""
    def get(self, key: Position | Tuple[int, int], default=None):
        if key in self:
            return self[key]
        return default

    def __setitem__(self, key: Position | Tuple[int, int], item):
        key = self.PositionToLocation(key)
        self.data[key] = item

    def __delitem__(self, key: Position | Tuple[int, int]):
        key = self.PositionToLocation(key)
        del self.data[key]

    def __getitem__(self, key: Position | Tuple[int, int]):
        key = self.PositionToLocation(key)
        if key in self.data:
            return self.data[key]
        if hasattr(self.__class__, "__missing__"):
            return self.__class__.__missing__(self, key)
        raise KeyError(key)

    def __contains__(self, key):
        key = self.PositionToLocation(key)
        return key in self.data

    def PositionToLocation(self, key: Position | Tuple[int, int]):
        if isinstance(key, Position):
            return key.location()
        else:
            assert isinstance(key, tuple) and len(key) == 2, f"Invalid key? {key}"
            return key

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
        self.path_table: PathReservation = PathReservation()

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
        constraints = self.path_table.get(position)

        if constraints is None:
            return

        constraint = constraints[timestep]

        if constraint is not None:
            assert constraint.agent_id == agent_id
            self.path_table[position][timestep] = None

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
        self.path_table: PathReservation = PathReservation()
        self.num_agents = num_agents

    def update_plan(self, extension: List[Tuple[int, Position]], agent_id: int):
        """
        Extends or create a path in the schedule table, enforcing the order??.

        Parameters:
        -----------
        agent_id : int
            The ID of the agent.
        path : List[Position]
            A list of positions that the agent will visit.
        """
        for timestep, position in extension:
            if position not in self.path_table:
                self.path_table[position] = deque()
            constraint = GridConstraint()
            constraint.agent_id = agent_id
            constraint.vertex = True
            constraint.edge = position.theta
            constraint.timestep_ = timestep

            self.path_table[position].append(constraint)


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
        schedule = self.path_table.get(position)
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
        constraints = self.path_table.get(position)

        if constraints is None or not constraints:
            return

        constraint = constraints[0]

        if constraint is not None:
            try:
                assert constraint.agent_id == agent_id, \
                                    f"Trying to delete agent {agent_id} on \
    constraint for {constraint.agent_id}. Execution order is messed up"
                assert constraint.timestep_ == timestep, f"Trying delete at time: {timestep} \
    for constraint at {constraint.timestep_}"
                constraints.popleft()
            except AssertionError:
                print(f"Skipping this removal for agent {agent_id} at time \
{timestep} with constraint time {constraint.timestep_}")


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
        print("------------------------\nCurrent schedule:\n")
        for loc, q in self.path_table.items():
            print(loc, end=": ")
            for constraint in q:
                print(f"[{constraint}, {constraint.timestep_}], ", end="")
            print()
        for timestep, position in path:
            print( f"Deleting {position} at time {timestep}, ")
            self.delete_entry(position, agent_id, timestep)
        print("------------------------\nAfter schedule:\n")
        for pair in self.path_table.items():
            print(pair)
