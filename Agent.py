
from typing import Dict, List, Tuple

from File_Handler import load_paths
from Position import Position
from Status import Status


class Agent:

    num_of_agents: int = 0

    # Class Attribute containing plans of all agents
    plans: Dict[int ,List[Position]] = None


    def __init__(self, filename: str):
        self.position: Position = None  # current position of agent 
        self.timestep: int = 0
        self._id: int = Agent.num_of_agents  # id corresponding to agents position in plans
        self.status: Status = Status.Waiting
        Agent.num_of_agents += 1

        if Agent.plans is None: self.load_paths(filename)

    def load_paths(self, filename: str):
        Agent.plans = load_paths(filename)

    def get_next_position(self):
        if self.timestep >= len(Agent.plans.get(self._id)):
            return None

        position = Agent.plans.get(self._id)[self.timestep]
        self.timestep += 1
        return position
    
    def get_plan(self):
        return Agent.plans.get(self._id)

    def view_position(self, timestep: int) -> Position:
        return Agent.plans.get(self._id)[timestep]
    
    def get_initial_position(self) -> Position:
        return Agent.plans.get(self._id)[0]
    
    def __str__(self) -> str:
        return f"ID: {self._id}, Status: {self.status}, Position: {self.position}, Timestep: {self.timestep}"
    

    