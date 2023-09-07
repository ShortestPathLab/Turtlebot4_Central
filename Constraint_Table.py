from typing import Dict, List

from Grid_Constraints import GridConstraint
from Position import Position


class ConstraintTable:

    def __init__(self, agent_plans: Dict[int, List[Position]]) -> None:
        
        self.path_table = {}

        for agent_id, agent_plan in agent_plans.items():
            self.add_path(agent_id, agent_plan)


    # This needs to be implemented in c++ its so gross how python handles this.
    def add_path(self, agent_id: int, path: List[Position]):

        for timestep, position in enumerate(path):
            if self.path_table .get((position.x, position.y)) is None:
                self.path_table[(position.x, position.y)] = []

            if len(self.path_table .get((position.x, position.y))) <= timestep:
                self.path_table [(position.x, position.y)].extend([None] * (timestep - len(self.path_table .get((position.x, position.y))) + 1))

            assert self.path_table.get((position.x, position.y))[timestep] is None

            constraint = GridConstraint()
            constraint.agent_id = agent_id
            constraint.v_ = True
            constraint.e_ = position.theta
            constraint.timestep_ = timestep

            self.path_table [(position.x, position.y)][timestep] = constraint


    def scheduled(self, position: int, agent_id: int) -> int:
  
        for constraint in self.path_table[(position.x, position.y)]:
            if constraint is None: continue
            return constraint.agent_id == agent_id

    
    def remove_path(self, agent_id: int, path: List[Position], timestep: int):

        for timestep, position in enumerate(path):
            self.delete_entry(position, agent_id, timestep)


    def delete_entry(self, position: Position, agent_id: int, timestep: int):
 
        constraint: GridConstraint = self.path_table.get((position.x, position.y))[timestep]

        if constraint is not None:
            assert constraint.agent_id == agent_id
        
        self.path_table.get((position.x,position.y))[timestep] = None

        
        
