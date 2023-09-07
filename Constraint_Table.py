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
            x, y, theta = position

            if self.path_table .get((x, y)) is None:
                self.path_table[(x, y)] = []

            if len(self.path_table .get((x, y))) <= timestep:
                self.path_table [(x, y)].extend([None] * (timestep - len(self.path_table .get((x, y))) + 1))

            assert self.path_table.get((x, y))[timestep] is None

            constraint = GridConstraint()
            constraint.agent_id = agent_id
            constraint.v_ = True
            constraint.e_ = theta
            constraint.timestep_ = timestep

            self.path_table [(x, y)][timestep] = constraint


    def scheduled(self, position: int, agent_id: int) -> int:
        x, y, theta = position    
        for constraint in self.path_table[(x,y)]:
            if constraint is None: continue
            return constraint.agent_id == agent_id

    
    def remove_path(self, agent_id: int, path: List[Position], timestep: int):

        for timestep, position in enumerate(path):
            self.delete_entry(agent_id, position, timestep)
            

    def delete_entry(self, position: Position, agent_id: int, timestep: int):

        x, y, theta = position    

        constraint: GridConstraint = self.path_table.get((x,y))[timestep]

        if constraint is not None:
            assert constraint.agent_id == agent_id
        
        self.path_table.get((x,y))[timestep] = None

        
        
