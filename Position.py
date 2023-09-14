from dataclasses import dataclass
from typing import Tuple


# Position Struct
@dataclass
class Position:
    x: float
    y: float
    theta: float

    def __repr__(self) -> str:
        return f"{self.x},{self.y},{self.theta}"
    
    def toTuple(self) -> Tuple:
        return (self.x, self.y, self.theta)