import abc
from typing import Dict, Tuple

from Position import Position


class ExecutionPolicy(abc.ABC):
    """
    Abstract base class for execution policies.
    """

    @abc.abstractmethod
    def get_next_position(self, agent_id: int) -> Tuple[Position, int]:
        """
        Abstract method to get the next position.

        Args:
            agent_id (int): The index of the current position.

        Returns:
            Tuple[Position, int]: The next position and the time to reach it.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, data: Dict) -> None:
        """
        Abstract method to update the execution policy.

        Args:
            data (Dict): The data to update the policy.
        """
        raise NotImplementedError

