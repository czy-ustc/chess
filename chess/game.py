# Author       : czy
# Description  : Initial chess pieces distribution.
#
# Copyright 2022 Zhiyuan Chen <chenzhiyuan@mail.ustc.edu.cn>

import json
from copy import deepcopy

from chess.constant import Color, Name
from chess.database import Database

# Standard chess pieces distribution.
standard = [
    # White
    [(Color.WHITE, Name.ROOK), [(1, 1)]],
    [(Color.WHITE, Name.KNIGHT), [(2, 1)]],
    [(Color.WHITE, Name.BISHOP), [(3, 1)]],
    [(Color.WHITE, Name.QUEEN), [(4, 1)]],
    [(Color.WHITE, Name.KING), [(5, 1)]],
    [(Color.WHITE, Name.BISHOP), [(6, 1)]],
    [(Color.WHITE, Name.KNIGHT), [(7, 1)]],
    [(Color.WHITE, Name.ROOK), [(8, 1)]],
    [(Color.WHITE, Name.PAWN), [(1, 2)]],
    [(Color.WHITE, Name.PAWN), [(2, 2)]],
    [(Color.WHITE, Name.PAWN), [(3, 2)]],
    [(Color.WHITE, Name.PAWN), [(4, 2)]],
    [(Color.WHITE, Name.PAWN), [(5, 2)]],
    [(Color.WHITE, Name.PAWN), [(6, 2)]],
    [(Color.WHITE, Name.PAWN), [(7, 2)]],
    [(Color.WHITE, Name.PAWN), [(8, 2)]],
    # Black
    [(Color.BLACK, Name.ROOK), [(1, 8)]],
    [(Color.BLACK, Name.KNIGHT), [(2, 8)]],
    [(Color.BLACK, Name.BISHOP), [(3, 8)]],
    [(Color.BLACK, Name.QUEEN), [(4, 8)]],
    [(Color.BLACK, Name.KING), [(5, 8)]],
    [(Color.BLACK, Name.BISHOP), [(6, 8)]],
    [(Color.BLACK, Name.KNIGHT), [(7, 8)]],
    [(Color.BLACK, Name.ROOK), [(8, 8)]],
    [(Color.BLACK, Name.PAWN), [(1, 7)]],
    [(Color.BLACK, Name.PAWN), [(2, 7)]],
    [(Color.BLACK, Name.PAWN), [(3, 7)]],
    [(Color.BLACK, Name.PAWN), [(4, 7)]],
    [(Color.BLACK, Name.PAWN), [(5, 7)]],
    [(Color.BLACK, Name.PAWN), [(6, 7)]],
    [(Color.BLACK, Name.PAWN), [(7, 7)]],
    [(Color.BLACK, Name.PAWN), [(8, 7)]],
]


class Game:
    """
    Create a new game according to the distribution of pieces.

    Parameters
    ----------
    pieces : list
        Chess pieces distribution.

    """
    def __init__(self, pieces: list = standard) -> None:
        # Format conversion.
        for index, (piece, place) in enumerate(pieces):
            for i, p in enumerate(place):
                # If the third value is omitted, the probability is 1.
                if len(p) != 3:
                    place[i] = (*p, 1)
                # Because the list cannot be hashed, 
                # it is uniformly converted to tuples.
                if not isinstance(place[i], tuple):
                    place[i] = tuple(place[i])

            # Convert to standard enumeration values.
            color = (
                piece[0]
                if isinstance(piece[0], Color)
                else eval(f"Color.{piece[0].upper()}")
            )
            name = (
                piece[1]
                if isinstance(piece[1], Name)
                else eval(f"Name.{piece[1].upper()}")
            )
            pieces[index][0] = (color, name)

        self._pieces = pieces

    @staticmethod
    def load(id: int) -> "Game":
        """Reload the endgame according to the `id`."""
        database = Database()
        data = database.load(id)
        for d in data:
            color = eval(f"Color.{d[0][0].upper()}")
            name = eval(f"Name.{d[0][1].upper()}")
            d[0] = [color, name]
        return Game(data)

    def dump(self) -> str:
        """Convert to standard JSON format."""
        data = deepcopy(self._pieces)
        for i in range(len(data)):
            data[i][0] = [d.name.lower() for d in data[i][0]]
        return json.dumps(data)

    def save(self, name: str, type_: int, turn: bool=False) -> int:
        """Save the chessboard to the database."""
        data = deepcopy(self._pieces)
        for i in range(len(data)):
            data[i][0] = [d.name.lower() for d in data[i][0]]

        database = Database()
        return database.save(data, name, type_, turn)

    @property
    def pieces(self) -> dict:
        """Return all pieces."""
        return self._pieces
