from typing import Dict, List, Tuple

from Agent import Agent
from Execution_Policy import ExecutionPolicy
from Position import Position
from Status import Status


class FSP(ExecutionPolicy):
    """
    A fully synchronized execution policy for multiple agents.

    Attributes:
    -----------
    agents : List[Agent]
        A list of Agent objects representing the agents in the system.
    current_timestep : int
        The current timestep of the system.

    Methods:
    --------
    get_next_position(index: int) -> Tuple[Position, int]:
        Returns the next position of the agent at the given index and the current timestep.
    update(data: Dict) -> None:
        Updates the position and status of the agent with the given data.
    """

    def __init__(self, plan_file: str, num_of_agents: int):
        """
        Initializes the FSP object.

        Parameters:
        -----------
        plan_file : str
            The path to the plan file for the agents.
        num_of_agents : int
            The number of agents in the system.
        """
        self.agents: List[Agent] = [Agent(plan_file) for _ in range(num_of_agents)]
        self.current_timestep: int = 0

    def get_next_position(self, agent_id: int) -> Tuple[Position, int]:
        """
        Returns the next position of the agent at the given index and the current timestep.

        Parameters:
        -----------
        index : int
            The index of the agent.

        Returns:
        --------
        Tuple[Position, int]
            A tuple containing the next position of the agent and the current timestep.
        """
        agent = self.agents[agent_id]

        if all(agent.status == Status.SUCCEEDED for agent in self.agents):
            self.current_timestep += 1
            agent.status = Status.EXECUTING

        return agent.view_position(self.current_timestep), self.current_timestep

    def update(self, data: Dict) -> None:
        """
        Updates the position and status of the agent with the given data.

        Parameters:
        -----------
        data : Dict
            A dictionary containing the data to update the agent with.
        """
        agent_id: int = data.get("agent_id")
        agent: Agent = self.agents[agent_id]  # Mutate Agent Data
        agent.position: Position = Position(*data.get("position"))
        agent.status: Status = Status.from_string(data.get("status"))

        if agent.status == Status.SUCCEEDED:
            agent.position = agent.view_position(agent.timestep)