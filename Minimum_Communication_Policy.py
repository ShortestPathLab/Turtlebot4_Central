from typing import List, Tuple, Dict

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

    def get_next_position(self, agent_id) -> Tuple[List[Position], Tuple[int, int]]:
        """
        Returns the next position and timestep for the given agent.

        Parameters:
        -----------
        agent_id : int
            The ID of the agent.

        Returns:
        --------
        Tuple[List[Position], Tuple[int, int]]
            A tuple containing the next positions and timestep for the given
            agent.
        """

        agent: Agent = self.agents[agent_id]

        if agent.position is None:
            start_position = agent.get_initial_position()
            end_timestep = 0
            return [start_position], (end_timestep, end_timestep)

        start_timestep = agent.timestep
        end_timestep = agent.timestep

        start_position = agent.view_position(end_timestep)
        target_positions: List[Position] = [start_position]
        # Join up to MAX_STEPS_INTO_FUTURE into a single motion
        while end_timestep + 1 < len(agent.get_plan()):
            next_timestep = end_timestep + 1
            next_position = agent.view_position(next_timestep)

            # Check if we are scheduled at the next position
            if not self.schedule_table.scheduled(next_position, agent_id):
                break

            # If we are next scheduled we an go to next position.
            end_timestep = next_timestep
            target_positions.append(next_position)

            # If the next position requires a turn we stay where we are.
            if start_position.theta != next_position.theta:
                break

        return target_positions, (start_timestep ,end_timestep)

    def update(self, data) -> None:
        """
        Updates the agent data.

        Parameters:
        -----------
        data : dict
            A dictionary containing the agent data.
        """
        agent_id: int | None = data.get("agent_id")

        if agent_id is None:
            print("Agent id was not provided, cannot update central controller")
            return

        agent: Agent = self.agents[agent_id]  #
        agent.status = Status.from_string(data.get("status"))

        if agent.status == Status.SUCCEEDED:

            pose: Dict[str, int] = data.get("position")
            if pose is None:
                print(f"Pose was not provided, by agent {agent_id}, cannot update")
                return
            if not all(map(lambda val: val in pose.keys(), ["x", "y", "theta"])):
                print(f"Pose is missing one of x, y, theta values for agent {agent_id}")
                return

            agent.timestep = data.get("timestep")
            agent.position = Position(pose["x"], pose["y"], pose["theta"])
            agent.position = agent.view_position(agent.timestep)
            plan = agent.get_plan()
            self.schedule_table.remove_path(agent_id, plan, agent.timestep)

        print(agent)

    def get_status(self) -> List[Tuple[int, Status]]:
        return [(agent._id, agent.status) for agent in self.agents]

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

    def get_next_position(self, agent_id: int) -> Tuple[List[Position], Tuple[int, int]]:

        agent: Agent = self.agents[agent_id]

        if agent.position is None:
            start_position = agent.get_initial_position()
            end_timestep = 0
            return [start_position], (end_timestep, end_timestep)

        start_timestep = agent.timestep
        end_timestep = agent.timestep

        start_position = agent.view_position(end_timestep)
        target_positions: List[Position] = [start_position]
        # Join up to MAX_STEPS_INTO_FUTURE into a single motion
        while end_timestep + 1 < len(agent.get_plan()):
            next_timestep = end_timestep + 1
            next_position = agent.view_position(next_timestep)

            # Check if we are scheduled at the next position
            if not self.schedule_table.scheduled(next_position, agent_id):
                break

            # If we are next scheduled we an go to next position.
            end_timestep = next_timestep
            target_positions.append(next_position)

            # If the next position requires a turn we stay where we are.
            if start_position.theta != next_position.theta:
                break

        return target_positions, (start_timestep ,end_timestep)

    def update(self, data) -> None:
        """
        Updates the agent data.

        Parameters:
        -----------
        data : dict
            A dictionary containing the agent data.
        """
        agent_id: int | None = data.get("agent_id")

        if agent_id is None:
            print("Agent id was not provided, cannot update central controller")
            return
        agent: Agent = self.agents[agent_id]  # Mutate Agent Data
        agent.status = Status.from_string(data.get("status"))



        if agent.status == Status.SUCCEEDED:
            pose: Dict[str, int] = data.get("position")
            if pose is None:
                print(f"Pose was not provided, by agent {agent_id}, cannot update")
                return
            if not all(map(lambda val: val in pose.keys(), ["x", "y", "theta"])):
                print(f"Pose is missing one of x, y, theta values for agent {agent_id}")
                return

            agent.position = Position(pose["x"], pose["y"], pose["theta"])
            prev_timestep = agent.timestep
            agent.timestep = data.get("timestep")
            agent.position = agent.view_position(agent.timestep)
            plan = agent.get_plan()
            ## Test whether this has off by one errors
            print("Checking timesteps for removal:")
            print(f"Previous: {prev_timestep} Current: {agent.timestep}")
            self.schedule_table.remove_path(
                                            agent_id,
                                            [*enumerate(plan[prev_timestep:agent.timestep],
                                                         prev_timestep + 1)]
                                            )

        print(agent)

    def get_agent_locations(self) -> Tuple[List[Tuple[Position, int]], bool]:
        """
        Method to get the final position of agents in the committed plan

        Returns:
            List[Tuple[Position, int]]: A list containing pairs of Position and the id of the agent there
        """
        agent_positions = []
        all_started = True
        for agent in self.agents:
            plan = agent.get_plan()
            if plan:
                agent_positions.append((plan[-1], agent._id))
            else:
                all_started = False
        return agent_positions, all_started

    def extend_plans(self, extensions: List[Tuple[int, List[Position]]], lookahead: int = 10) -> None:
        """
        Extend the existing plans for agents

        Args:
            extensions:
                List[Tuple[int, List[Tuple[Position, int]]]]:
                    A list containing pairs of agent_id and plan extensions,
                    where plan extensions are tuples of Position and timestep to reach it
        """
        for (agent_id, extension) in extensions:
            if not (0 <= agent_id < len(self.agents)):
                print("Not a valid agent id, ignoring")
                continue
            agent = self.agents[agent_id]
            # Commit up to {lookahead} steps for this agent, ignoring further extensions
            (len(agent.get_plan()) - agent.timestep)
            extension = extension[:lookahead - (len(agent.get_plan()) - agent.timestep)]
            for next_pos in extension:
                if agent.plans is None:
                    raise ValueError("Plans were not initialised")

                agent.plans[agent_id].append(next_pos)

            self.schedule_table.update_plan([*enumerate(extension, len(agent.get_plan()))], agent_id)
            print(f"Agent {agent_id}:", agent.plans[agent_id][-15:]) # type: ignore
        # print(agent.plans)

    def get_status(self) -> List[Tuple[int, Status]]:
        return [(agent._id, agent.status) for agent in self.agents]

if __name__ == "__main__":
    mcp = OnlineMCP(2)
    plan = [(0, [Position(0,0,0)]), (1, [Position(0,1,0)]), (0, [Position(0,1,180)]), (1, [Position(1,1,180)])] # noqa: E501
    mcp.extend_plans(plan)
    for q in mcp.schedule_table.path_table.items():
        print(q)
    print("Agent 0 moves once")

    def extract(x: tuple[int, List[Position]]):
        return x[1][0]

    try:
        mcp.schedule_table.remove_path(0,
                                   [*enumerate(map(extract, plan[0:1]), 1)])
    except AssertionError as ex:
        print(ex) # Expect an error on deleting the 2nd constraint on (0, 1) for agent 1
    for b in mcp.schedule_table.path_table.items():
        print(b)
    print("Agent 1 moves once")
    mcp.schedule_table.remove_path(1, [*enumerate(map(extract,plan[1:2]), 1)])
    for c in mcp.schedule_table.path_table.items():
        print(c)
    print("Then agent 0 moves again")
    mcp.schedule_table.remove_path(0, [*enumerate(map(extract,plan[2:3]), 2)])
    print("Now Agent 1 takes final move")
    for d in mcp.schedule_table.path_table.items():
        print(d)
        mcp.schedule_table.remove_path(1, [*enumerate(map(extract,plan[3:4]), 2)])
    print("After removing")
    for e in mcp.schedule_table.path_table.items():
        print(e)
