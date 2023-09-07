from enum import Enum


class Status(Enum):
    Failed = 0
    Executing = 1
    Succeeded = 2
    Waiting = 3
    Aborted = 4
    
    @classmethod
    def value_of(cls, value):
        for k, v in cls.__members__.items():
            if k == value:
                return v
        else:
            raise ValueError(f"'{cls.__name__}' enum not found for '{value}'")
