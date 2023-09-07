from dataclasses import dataclass

# Struct like class
@dataclass
class Position:
    x: float
    y: float
    theta: float