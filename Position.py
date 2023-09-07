from dataclasses import dataclass
import json 

# Struct like class
@dataclass
class Position:
    x: float
    y: float
    theta: float

    def __repr__(self) -> str:
        return f"{self.x},{self.y},{self.theta}"
    
    def toTuple(self):
        return (self.x, self.y, self.theta)