import abc
from typing import Dict, Tuple

from Position import Position


class ExecutionPolicy(abc.ABC):

    @abc.abstractmethod
    def get_next_position(self, index: int) -> Tuple[Position, int]:
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, data: Dict) -> None:
        raise NotImplementedError
        
