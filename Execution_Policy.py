import abc
from typing import List, Dict

from Agent import Agent
from Position import Position
from Status import Status

class ExecutionPolicy(abc.ABC):

    @abc.abstractmethod
    def get_next_position(self, index: int) -> Position:
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, data: Dict):
        raise NotImplementedError
    