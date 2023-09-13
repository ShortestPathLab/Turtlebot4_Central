from typing import Dict, List

from Agent import Agent
from Execution_Policy import ExecutionPolicy
from Position import Position
from Status import Status


class FSP(ExecutionPolicy):

    def __init__(self, plan_file: str, num_of_agents: int):

        self.agents: List[Agent] = [Agent(plan_file) for _ in range(num_of_agents)]
        self.current_timestep: int = 0

    def get_next_position(self, index: int) -> Position:

        agent = self.agents[index]

        if all(agent.status == Status.Succeeded for agent in self.agents):
            self.current_timestep += 1
            agent.status = Status.Executing
            
        return agent.view_position(self.current_timestep), self.current_timestep
          
    def update(self, data: Dict):

        agent_id: int = data.get("agent_id")
        agent: Agent = self.agents[agent_id]  # Mutate Agent Data
        agent.position: Position = Position(*data.get("position"))
        agent.status: Status = Status.value_of(data.get("status"))

        if agent.status == Status.Succeeded:
            agent.position = agent.view_position(agent.timestep)