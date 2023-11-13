from enum import Enum


class Status(Enum):
    """
    Enum class representing the status of a task.
    """

    FAILED = 0
    EXECUTING = 1
    SUCCEEDED = 2
    WAITING = 3
    ABORTED = 4

    @classmethod
    def from_string(cls, string: str):
        """
        Returns the enum value corresponding to the given string.

        Args:
            string (str): The string representation of the enum value.

        Returns:
            The enum value corresponding to the given string.

        Raises:
            ValueError: If the given string does not correspond to any enum
            value.
        """
        for k, v in cls.__members__.items():
            if k.lower() == string.lower():
                return v

        raise ValueError(f"'{cls.__name__}' enum not found for '{string}'")

    def __str__(self):
        """
        Returns the string representation of the enum value.

        Returns:
            The string representation of the enum value.
        """
        return self.name
