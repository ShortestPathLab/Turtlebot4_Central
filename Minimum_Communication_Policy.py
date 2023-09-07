from typing import List, Tuple

from Agent import Agent
from Constraint_Table import ConstraintTable
from Execution_Policy import Execution_Policy
from Position import Position
from Status import Status


class MCP(Execution_Policy):

    def __init__(self, plan_file: str, num_of_agents: int) -> None:
        self.agents: List[Agent]  = [Agent(plan_file) for _ in num_of_agents]
        self.constraint_table: ConstraintTable = ConstraintTable(Agent.plans)


    def get_next_position(self, agent_id) -> Tuple[Position, int]:
               
        agent: Agent = self.agents[agent_id]

        # Send Robot to Initial Position
        if agent.position is None:
            position = agent.get_initial_position()
            timestep = 0
            return position, timestep


        next_timestep = agent.timestep
        initial_position = agent.position

        #Do While Loop 
        while True:

            # Check if we are required to turn
            next_position = agent.view_position(next_timestep)
            if initial_position.theta != next_position.theta: break

            # Check if we are scheduldd at the next position
            future_timestep = next_timestep + 1
            if future_timestep < len(agent.get_plan()) and \
                not self.constraint_table.scheduled(agent.view_position(future_timestep), agent_id): break
            
            # Stop Condition
            if next_timestep + 1 >= len(agent.get_plan()): break
            next_timestep += 1
        
        agent.timestep = next_timestep

        return next_position, timestep


    def update(self, data):
         
        agent_id: int = data.get("agent_id")
        agent: Agent = self.agents[agent_id]  # Mutate Agent Data

        agent.position: Position = data.get("position")
        agent.status: Status = Status.value_of(data.get("status"))

        if agent.status == Status.Succeeded:
            agent.timestep
            agent.position = agent.view_position(agent.timestep)
            self.constraint_table.delete_path(agent_id, agent.get_plan(), agent.timestep)

        print(agent)