from datetime import date, datetime, time
from enum import Enum


class TaskType(Enum):
    CREATE_TABLE = 1
    INSERT = 2
    QUERY = 3
    UPDATE = 4
    DELETE = 5


class DataType(Enum):
    String = str
    Integer = int
    Float = float
    Boolean = bool
    Date = date
    Time = time
    DateTime = datetime


class ON_DELETE(Enum):
    CASCADE = 1
    PROTECT = 2
    SET_NULL = 3
    SET_DEFAULT = 4
    SET = 5


class When(Enum):
    BEFORE = 1
    AFTER = 2


class Event(Enum):
    INSERT = 1
    UPDATE = 2
    DELETE = 3
