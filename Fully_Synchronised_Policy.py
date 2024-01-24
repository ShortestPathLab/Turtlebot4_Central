from typing import Dict, List, Tuple

from Agent import Agent, OnlineAgent
from Execution_Policy import ExecutionPolicy, OnlineExecutionPolicy
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
        Returns the next position of the agent at the given index
        and the current timestep.
    update(data: Dict) -> None:
        Updates the position and status of the agent with the given data.
    """

    def __init__(self, plan_file: str, num_agent: int):
        """
        Initializes the FSP object.

        Parameters:
        -----------
        plan_file : str
            The path to the plan file for the agents.
        num_of_agents : int
            The number of agents in the system.
        """
        self.agents: List[Agent] = [Agent(plan_file) for _ in range(num_agent)]
        self.timestep: int = 0

    def get_next_position(self, agent_id: int) -> Tuple[List[Position], Tuple[int, int]]:
        """
        Returns the next position of the agent at the given index and the
        current timestep.

        Parameters:
        -----------
        index : int
            The index of the agent.

        Returns:
        --------
        Tuple[Position, int]
            A tuple containing the next position of the agent and the
            current timestep.
        """
        agent = self.agents[agent_id]
        start_timestep = self.timestep

        if all(agent.status == Status.SUCCEEDED for agent in self.agents):
            self.timestep += 1
            agent.status = Status.EXECUTING

        return [agent.view_position(self.timestep)], (start_timestep, self.timestep)

    def update(self, data: Dict) -> None:
        """
        Updates the position and status of the agent with the given data.

        Parameters:
        -----------
        data : Dict
            A dictionary containing the data to update the agent with.
        """
        if "agent_id" not in data:
            print("Error: Agent ID not found in data.")
            exit(1)

        agent_id: int = data["agent_id"]
        agent: Agent = self.agents[agent_id]  # Mutate Agent Data

        if "position" not in data:
            print("Error: Position not found in data.")
            exit(1)

        agent.position = Position(*data["position"])

        if "status" not in data:
            print("Error: Status not found in data.")
            exit(1)

        agent.status = Status.from_string(data["status"])

        if agent.status == Status.SUCCEEDED:
            agent.position = agent.view_position(agent.timestep)


class OnlineFSP(OnlineExecutionPolicy):
    """
    A fully synchronized execution policy for multiple agents supporting extension of plans.

    Attributes:
    -----------
    agents : List[Agent]
        A list of Agent objects representing the agents in the system.
    current_timestep : int
        The current timestep of the system.

    Methods:
    --------
    get_next_position(index: int) -> Tuple[Position, int]:
        Returns the next position of the agent at the given index
        and the current timestep.
    update(data: Dict) -> None:
        Updates the position and status of the agent with the given data.
    """

    def __init__(self, num_agents: int):
        """
        Initializes the FSP object.

        Parameters:
        -----------
        num_of_agents : int
            The number of agents in the system.
        """

        self.agents: List[OnlineAgent] = [OnlineAgent() for _ in range(num_agents)]
        for agent in self.agents:
            if agent.plans is not None:
                agent.plans.setdefault(agent._id, [])
            else:
                raise ValueError("Plans were not intialised")
        self.timestep: int = 0

    def extend_plans(self, extensions: List[Tuple[int, List[Position]]]) -> None:
        """
        Extend the existing plans for agents

        Args:
            extensions:
                List[Tuple[int, List[Tuple[Position, int]]]]:
                    A list containing pairs of agent_id and plan extensions,
                    where plan extensions are tuples of Position and timestep to reach it
        """
        for (agent_id, extension) in extensions:
            agent = self.agents[agent_id]
            # print(agent.plans)
            for next_pos in extension:
                if agent.plans is not None:
                    agent.plans[agent_id].append(next_pos)
                else:
                    raise ValueError("Plans were not initialised")
        print(agent.plans)

    def get_agent_locations(self) -> Tuple[List[Tuple[Position, int]], bool]:
        """
        Method to get the final positions of agents;
            this policy assumes agents will complete their plans fully synchronised
            so it returns the last planned location of each agent

        Returns:
            List[Tuple[Position, int]]: A list containing pairs of Position and the id of the agent there
        """
        agent_positions = []
        all_started = True
        for agent in self.agents:
            plan = agent.get_plan()
            if plan:
                agent_positions.append((agent.get_plan()[-1], agent._id))
            else:
                all_started = False
        return agent_positions, all_started

    def get_next_position(self, agent_id: int) -> Tuple[List[Position], Tuple[int, int]]:
        """
        Returns the next position of the agent at the given index and the
        current timestep.

        Parameters:
        -----------
        index : int
            The index of the agent.

        Returns:
        --------
        Tuple[Position, int]
            A tuple containing the next position of the agent and the
            current timestep.
        """
        agent = self.agents[agent_id]
        start_timestep = self.timestep
        if all(agent.status == Status.SUCCEEDED for agent in self.agents):
            self.timestep += 1
            agent.status = Status.EXECUTING

        return [agent.view_position(self.timestep)], (start_timestep, self.timestep)

    def update(self, data: Dict) -> None:
        """
        Updates the position and status of the agent with the given data.

        Parameters:
        -----------
        data : Dict
            A dictionary containing the data to update the agent with.
        """
        if "agent_id" not in data:
            print("Error: Agent ID not found in data.")
            exit(1)

        agent_id: int = data["agent_id"]
        agent: Agent = self.agents[agent_id]  # Mutate Agent Data

        if "position" not in data:
            print("Error: Position not found in data.")
            exit(1)

        agent.position = Position(*data["position"])

        if "status" not in data:
            print("Error: Status not found in data.")
            exit(1)

        agent.status = Status.from_string(data["status"])

        if agent.status == Status.SUCCEEDED:
            agent.position = agent.view_position(agent.timestep)
