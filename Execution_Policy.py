import abc
from typing import Dict

from Position import Position


class ExecutionPolicy(abc.ABC):

    @abc.abstractmethod
    def get_next_position(self, index: int) -> Position:
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, data: Dict):
        raise NotImplementedError
        
