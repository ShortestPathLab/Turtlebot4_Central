from typing import List, Tuple

from Agent import Agent
from Execution_Policy import ExecutionPolicy
from Position import Position
from Schedule_Table import ScheduleTable
from Status import Status


class MCP(ExecutionPolicy):

    def __init__(self, plan_file: str, num_of_agents: int) -> None:
        self.agents: List[Agent]  = [Agent(plan_file) for _ in range(num_of_agents)]
        self.constraint_table: ScheduleTable = ScheduleTable(Agent.plans)


    def get_next_position(self, agent_id) -> Tuple[Position, int]:
               
        agent: Agent = self.agents[agent_id]

        # Send Robot to Initial Position
        if agent.position is None:
            position = agent.get_initial_position()
            timestep = 0
            return position, timestep


        timestep = agent.timestep
        position = agent.position

        while timestep+1 < len(agent.get_plan()):

            next_timestep = timestep+1
            next_position = agent.view_position(next_timestep)

            # Check if we are scheduled at the next position
            if next_timestep < len(agent.get_plan()) and \
                not self.constraint_table.scheduled(next_position, agent_id): break
            
            # If we are next scheduled we an go to next position. 
            timestep, position = next_timestep, next_position
            
            # If the next position requires a turn we stay where we are.
            if agent.position.theta != next_position.theta: break
            
            timestep+=1
        

        agent.timestep = timestep
        return position, timestep


    def update(self, data):

        agent_id: int = data.get("agent_id")
        agent: Agent = self.agents[agent_id]  # Mutate Agent Data
        agent.position: Position = Position(*data.get("position"))
        agent.status: Status = Status.from_string(data.get("status"))

        if agent.status == Status.Succeeded:
            agent.position = agent.view_position(agent.timestep)
            self.constraint_table.remove_path(agent_id, agent.get_plan(), agent.timestep)
         
