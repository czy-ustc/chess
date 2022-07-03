# Author       : czy
# Description  : Several enumeration constants.
#
# Copyright 2022 Zhiyuan Chen <chenzhiyuan@mail.ustc.edu.cn>

from enum import Enum

class Color(Enum):
    """
    The white player is marked as `WHITE`, 
    and the black player is marked as `BLACK`.
    """
    WHITE = 0
    BLACK = 1


class Name(Enum):
    """Standard names of various pieces."""
    KING = 0
    QUEEN = 1
    ROOK = 2
    BISHOP = 3
    KNIGHT = 4
    PAWN = 5


class State(Enum):
    """The state of a grid when judging chess."""
    UNOCCUPIED = 0
    REACHABLE = 1
    UNREACHABLE = 2


class Winner(Enum):
    """The winner of the game."""
    DRAW = -1
    NULL = 0
    WHITE = 1
    BLACK = 2

    def __bool__(self):
        """Return False when the game is not over."""
        return self != Winner.NULL
