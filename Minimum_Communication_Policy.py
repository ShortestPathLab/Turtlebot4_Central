from typing import List, Tuple

from Agent import Agent
from Execution_Policy import ExecutionPolicy
from Position import Position
from Schedule_Table import ScheduleTable
from Status import Status


class MCP(ExecutionPolicy):
    """
    A class representing the Minimum Communication Policy for a Central
    Controller.

    Attributes:
    -----------
    agents : List[Agent]
        A list of agents.
    schedule_table : ScheduleTable
        A schedule table for the agents.

    Methods:
    --------
    get_next_position(agent_id: int) -> Tuple[Position, int]:
        Returns the next position and timestep for the given agent.
    update(data) -> None:
        Updates the agent data.
    """

    def __init__(self, plan_file: str, num_agent: int) -> None:
        """
        Initializes the MCP class.

        Parameters:
        -----------
        plan_file : str
            The file containing the plan for the agents.
        num_of_agents : int
            The number of agents.
        """
        self.agents: List[Agent] = [Agent(plan_file) for _ in range(num_agent)]

        if Agent.plans is None:
            print("Error: Plans have not been loaded.")
            exit(1)

        self.schedule_table: ScheduleTable = ScheduleTable(Agent.plans)

    def get_next_position(self, agent_id) -> Tuple[Position, int]:
        """
        Returns the next position and timestep for the given agent.

        Parameters:
        -----------
        agent_id : int
            The ID of the agent.

        Returns:
        --------
        Tuple[Position, int]
            A tuple containing the next position and timestep for the given
            agent.
        """

        agent: Agent = self.agents[agent_id]

        # Send Robot to Initial Position
        if agent.position is None:
            position = agent.get_initial_position()
            timestep = 0
            return position, timestep

        timestep = agent.timestep
        position = agent.view_position(timestep)
        while timestep + 1 < len(agent.get_plan()):
            next_timestep = timestep + 1
            next_position = agent.view_position(next_timestep)

            # Check if we are scheduled at the next position
            if not self.schedule_table.scheduled(next_position, agent_id):
                break

            # If we are next scheduled we an go to next position.
            timestep = next_timestep
            position = next_position

            # If the next position requires a turn we stay where we are.
            if agent.view_position(agent.timestep).theta != position.theta:
                break

        return position, timestep

    def update(self, data) -> None:
        """
        Updates the agent data.

        Parameters:
        -----------
        data : dict
            A dictionary containing the agent data.
        """
        agent_id: int = data.get("agent_id")
        agent: Agent = self.agents[agent_id]  # Mutate Agent Data
        agent.position = Position(*data.get("position"))
        agent.status = Status.from_string(data.get("status"))
        agent.timestep = data.get("timestep")

        if agent.status == Status.SUCCEEDED:
            agent.position = agent.view_position(agent.timestep)
            plan = agent.get_plan()
            self.schedule_table.remove_path(agent_id, plan, agent.timestep)

        print(agent)
