from typing import List, Tuple

from Agent import Agent, OnlineAgent
from Execution_Policy import ExecutionPolicy, OnlineExecutionPolicy
from Position import Position
from Schedule_Table import ScheduleTable, OnlineSchedule
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

class OnlineMCP(OnlineExecutionPolicy):
    def __init__(self, num_agents: int):
        self.agents: List[OnlineAgent] = [OnlineAgent() for _ in range(num_agents)]
        for agent in self.agents:
            if agent.plans is not None:
                agent.plans.setdefault(agent._id, [])
            else:
                raise ValueError("Plans were not intialised")
        self.timestep: int = 0
        self.schedule_table = OnlineSchedule(num_agents)

    def get_next_position(self, agent_id: int) -> Tuple[Position, int]:
        agent: Agent = self.agents[agent_id]
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
        prev_timestep = agent.timestep
        agent.timestep = data.get("timestep")

        if agent.status == Status.SUCCEEDED:
            agent.position = agent.view_position(agent.timestep)
            plan = agent.get_plan()
            ## Test whether this has off by one errors
            print("Checking timesteps for removal:")
            print(f"Previous: {prev_timestep} Current: {agent.timestep}")
            self.schedule_table.remove_path(
                                            agent_id,
                                            [*enumerate(plan[:agent.timestep+1], 1)]
                                            )

        print(agent)

    def get_agent_locations(self) -> List[Tuple[Position, int]]:
        """
        Method to get the final position of agents in the committed plan

        Returns:
            List[Tuple[Position, int]]: A list containing pairs of Position and the id of the agent there
        """
        agent_positions = []
        for agent in self.agents:
            agent_positions.append((agent.get_plan()[-1], agent._id))
        return agent_positions

    def extend_plans(self, extensions: List[Tuple[int, List[Tuple[Position, int]]]]) -> None:
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

            ### NOTE: The following code describes what part of the extension is
            ###        committed for the execution policy
            for (next_pos, timestep) in extension: # Commit to the entire extension
                if agent.plans is not None:
                    if len(agent.plans[agent_id]) < timestep -  1: # This is fine?
                        raise ValueError("Trying to change existing plan or create undefined timestep")
                    agent.plans[agent_id].append(next_pos)
                else:
                    raise ValueError("Plans were not initialised")
            self.schedule_table.update_plan(extension, agent_id)

        print(agent.plans)


if __name__ == "__main__":
    mcp = OnlineMCP(2)
    plan = [(0, [(Position(0,0,0), 1)]), (1, [(Position(0,1,0), 1)]), (0, [(Position(0,1,180), 2)]), (1, [(Position(1,1,180), 2)])] # noqa: E501
    mcp.extend_plans(plan)
    for q in mcp.schedule_table.path_table.items():
        print(q)
    print("Agent 0 moves once")
    try:
        mcp.schedule_table.remove_path(0,
                                   [*enumerate(map(lambda x: x[1][0][0],plan[0:1]), 1)])
    except AssertionError as e:
        print(e) # Expect an error on deleting the 2nd constraint on (0, 1) for agent 1
    for b in mcp.schedule_table.path_table.items():
        print(b)
    print("Agent 1 moves once")
    mcp.schedule_table.remove_path(1, [*enumerate(map(lambda x: x[1][0][0],plan[1:2]), 1)])
    for c in mcp.schedule_table.path_table.items():
        print(c)
    print("Then agent 0 moves again")
    mcp.schedule_table.remove_path(0, [*enumerate(map(lambda x: x[1][0][0],plan[2:3]), 2)])
    print("Now Agent 1 takes final move")
    for d in mcp.schedule_table.path_table.items():
        print(d)
        mcp.schedule_table.remove_path(1, [*enumerate(map(lambda x: x[1][0][0],plan[3:4]), 2)])
    print("After removing")
    for e in mcp.schedule_table.path_table.items():
        print(e)
