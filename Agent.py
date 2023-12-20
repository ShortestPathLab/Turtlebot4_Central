from typing import Dict, List

from File_Handler import load_paths
from Position import Position
from Status import Status


class Agent:
    """
    Class representing an agent in a multi-agent system.

    Attributes:
    - position (Position): current position of the agent
    - timestep (int): current timestep of the agent
    - _id (int): id corresponding to agent's position in plans
    - status (Status): status of the agent
    """

    # Class Attribute containing plans of all agents
    plans: Dict[int, List[Position]] | None = None
    num_agents: int = 0

    def __init__(self, filename: str):
        """
        Initializes an Agent object.

        Args:
        - filename (str): name of the file containing the agent's plan
        """
        self.position: Position | None = None
        self.timestep: int = 0
        self._id: int = Agent.num_agents
        self.status: Status = Status.WAITING
        Agent.num_agents += 1

        if Agent.plans is None:
            self.load_paths(filename)

    def load_paths(self, filename: str) -> None:
        """
        Loads the plans of all agents from a file.

        Args:
        - filename (str): name of the file containing the plans
        """
        Agent.plans = load_paths(filename)

    def get_next_position(self) -> Position | None:
        """
        Returns the next position of the agent.

        Returns:
        - Position: the next position of the agent
        """
        if Agent.plans is None:
            print("Error: Plans have not been loaded.")
            exit(1)

        if self.timestep >= len(Agent.plans[self._id]):
            return None

        position = Agent.plans[self._id][self.timestep]
        self.timestep += 1
        return position

    def get_plan(self) -> List[Position]:
        """
        Returns the plan of the agent.

        Returns:
        - List[Position]: the plan of the agent
        """
        if Agent.plans is None:
            print("Error: Plans have not been loaded.")
            exit(1)

        return Agent.plans[self._id]

    def view_position(self, timestep: int) -> Position:
        """
        Returns the position of the agent at a given timestep.

        Args:
        - timestep (int): the timestep to view the position at

        Returns:
        - Position: the position of the agent at the given timestep
        """
        if Agent.plans is None:
            print("Error: Plans have not been loaded.")
            exit(1)
        if timestep >= len(Agent.plans[self._id]): # Plan is finished
            return Agent.plans[self._id][-1] # Show at end of plan if finished plan (lifelong model)
        return Agent.plans[self._id][timestep]

    def get_initial_position(self) -> Position:
        """
        Returns the initial position of the agent.

        Returns:
        - Position: the initial position of the agent
        """
        if Agent.plans is None:
            print("Error: Plans have not been loaded.")
            exit(1)

        return Agent.plans[self._id][0]

    def __str__(self) -> str:
        """
        Returns a string representation of the agent.

        Returns:
        - str: a string representation of the agent
        """
        return f"ID: {self._id}, \
            Status: {self.status}, \
            Position: {self.position}, \
            Timestep: {self.timestep}"

class OnlineAgent(Agent):
    """
    Class representing an agent in a multi-agent system, where the plan is extended during runtime
    This means the plans are initialised as an empty list
    Attributes:
    - position (Position): current position of the agent
    - timestep (int): current timestep of the agent
    - _id (int): id corresponding to agent's position in plans
    - status (Status): status of the agent
    """
    def __init__(self) -> None:
        """
        Initializes an Agent object.

        Args:
        - filename (str): name of the file containing the agent's plan
        """
        self.position: Position | None = None
        self.timestep: int = 0
        self._id: int = Agent.num_agents
        self.status: Status = Status.WAITING
        Agent.num_agents += 1

        if Agent.plans is None:
            Agent.plans = dict()
