from Execution_Policy import OnlineExecutionPolicy
from typing import Tuple, List, Dict
from Position import Position
from Agent import OnlineAgent
from Status import Status

class UnitExecutionPolicy(OnlineExecutionPolicy):
    """
    Single step execution policy that tracks actions status
    """
    def __init__(self, num_of_agents: int) -> None:
        self.next_states: List[Position] = [None for _ in range(num_of_agents)] # type: ignore
        self.curr_states: List[Position] = [None for _ in range(num_of_agents)] # type: ignore
        self.agents: List[OnlineAgent] = [OnlineAgent() for _ in range(num_of_agents)]
        for agent in self.agents:
            if agent.plans is not None:
                agent.plans.setdefault(agent._id, [])
            else:
                raise ValueError("Plans were not initialised")
        self.timestep = 0
        self.status = [Status.WAITING for _ in range(num_of_agents)]

    def get_next_position(self, agent_id: int) -> Tuple[List[Position], Tuple[int, int]]:
        """
        Method to get the next position. This class will only ever return a single next position

        Args:
            agent_id (int): The index of the current position.

        Returns:
            Tuple[List[Position], Tuple[int,int]]: The next positions and the start and end timesteps
        """
        if self.next_states[agent_id] is None:
            if self.curr_states[agent_id] is None:
                print(f"Current state for agent {agent_id} is None, aborting")
                exit(1)
            return [self.curr_states[agent_id]], (self.timestep, self.timestep)
        # It does not matter what is going on, the planner guarantees you can move safely from
        # curr_states to next_states.
        return [self.next_states[agent_id]], (self.timestep, self.timestep + 1)

        # match self.status[agent_id]:
        #     case Status.SUCCEEDED:
        #         return [self.next_states[agent_id]], (self.timestep, self.timestep)
        #     case Status.EXECUTING:
        #         print("Unknown why next location was requested while executing movement")
        #         return [self.next_states[agent_id]], (self.timestep, self.timestep)
        #     case _:
        #         # Failed to act, returning to initial location before current action
        #         return [self.curr_states[agent_id]], (self.timestep, self.timestep)

    def update(self, data: Dict) -> None:
        """
        Method to update the execution policy with agent's progress

        Args:
            data (Dict): The data to update the policy.
        """
        agent_id: int | None = data.get("agent_id")

        if agent_id is None:
            print("Agent id was not provided, cannot update central controller")
            return
        agent: OnlineAgent = self.agents[agent_id]  # Mutate Agent Data

        status: str | None = data.get("status")
        if status is None:
            print("Agent status was not provided")
            status = "FAILED"
        else:
            agent.status = Status.from_string(status)
            self.status[agent_id] = Status.from_string(status)


        # Update position and timestep
        # See pose JSON
        pose = data.get("position") # type: ignore
        if pose is None:
            print(f"Pose was not provided, by agent {agent_id}, cannot update")
            return
        if not all(map(lambda val: val in pose.keys(), ["x", "y", "theta"])):
            print(f"Pose is missing one of x, y, theta values for agent {agent_id}")
            return

        agent.position = Position(pose["x"], pose["y"], pose["theta"])
        agent.timestep = int(data.get("timestep")) # type: ignore

    def get_agent_locations(self) -> Tuple[List[Tuple[Position, int]], bool]:
        """
        Method to get the current positions of agents to plan on

        Returns:
            List[Tuple[Position, int]]: A list containing pairs of Position and the id of the agent there
        """
        agent_positions: List[Tuple[Position, int]] = []
        all_started = True
        for agent in self.agents:
            if self.curr_states[agent._id]:
                agent_positions.append((self.curr_states[agent._id], agent._id))
            else:
                all_started = False
                return agent_positions, all_started
        return agent_positions, all_started

    def extend_plans(
        self, extensions: List[Tuple[int, List[Position]]]
    ) -> None:
        """
        Abstract method to extend plans of agents without changing existing plans
        TODO: Consider changing incomplete plans? Commit windows...

        Args:
            extensions:
                List[Tuple[int, List[Tuple[Position, int]]]]:
                    A list containing pairs of agent_id and plan extensions,
                    where plan extensions are tuples of Position and timestep to reach it
        """
        next_states: List[Position | None] = [None]*len(self.agents)
        for (agent_id, extension) in extensions:
            if not (0 <= agent_id < len(self.agents)):
                print(f"Not a valid agent id {agent_id}, ignoring")
                continue
            agent = self.agents[agent_id]
            assert(len(extension) == 1), f"Extension is wrong length for UnitExecutionPolicy, \
                                             expected {1}, received {len(extension)}"

            next_pos = extension[0]
            if agent.plans is None:
                raise ValueError("Plans were not initialised for agents")
            else:
                agent.plans[agent_id].append(next_pos)
            next_states[agent_id] = next_pos

        for agent_id, state in enumerate(next_states):
            if state is None:
                print(f"Agent {agent_id} was not given a plan, repairing with WAIT")
                next_states[agent_id] = self.curr_states[agent_id]
        # Advance self.curr_states to self.next_states and insert new next_states
        self.status = [Status.EXECUTING]*len(self.agents)
        self.curr_states = self.next_states
        self.next_states = next_states # type: ignore

    def get_status(self) -> List[Tuple[int, Status]]:
        return [*enumerate(self.status)]
