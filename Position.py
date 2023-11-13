from dataclasses import dataclass

# Position Struct
from typing import Tuple


@dataclass
class Position:
    """
    A class representing a position in 3D space.

    Attributes:
    -----------
    x : float
        The x-coordinate of the position.
    y : float
        The y-coordinate of the position.
    theta : float
        The angle of the position in radians.

    Methods:
    --------
    __repr__() -> str
        Returns a string representation of the position in the format
        "x,y,theta".
    to_tuple() -> Tuple
        Returns a tuple representation of the position in the format
        (x, y, theta).
    """

    x: float
    y: float
    theta: float

    def __repr__(self) -> str:
        return f"{self.x},{self.y},{self.theta}"

    def to_tuple(self) -> Tuple:
        """
        Returns a tuple representation of the Position object.

        Returns:
        Tuple: A tuple containing the x, y, and theta values of the Position
        object.
        """
        return (self.x, self.y, self.theta)

    def __hash__(self) -> int:
        """
        Returns a unique hash value for the Position object based on its x and
        y coordinates.

        Returns:
        int: A unique hash value for the Position object.
        """
        return hash((self.x, self.y))
