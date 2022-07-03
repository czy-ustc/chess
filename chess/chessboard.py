# Author       : czy
# Description  : ChessBoard used for chess move generation/validation,
#                piece placement/movement, and check.
#
# Copyright 2022 Zhiyuan Chen <chenzhiyuan@mail.ustc.edu.cn>

import copy
from collections import defaultdict
from typing import Any, Iterator, List, Optional, Tuple

from chess.constant import Color, Name, Winner
from chess.database import Database
from chess.evaluate import *
from chess.game import Game
from chess.piece import Piece
from chess.rule import ActionRule, SpecialMoveRule
from chess.settings import setting


class ChessBoard:
    """
    Checkerboard object, which encapsulates functions
    such as move generation/validation, piece placement/movement and check.

    Parameters
    ----------
    game : Game
        Initial chess pieces distribution.

    """

    def __init__(self, game: Game) -> None:
        # Convert dict type pieces to Piece type.
        self.init_piece(game.pieces)
        # The place distribution of chess pieces is transformed
        # into the distribution of chess pieces on the chessboard.
        self.place_piece()

        # Whose turn is it to play chess.
        self.color = Color.WHITE
        # Chess record.
        self.record = ""

    def init_piece(self, pieces) -> None:
        """Convert dict type pieces to Piece type."""
        self.pieces = [Piece(piece[0][0], piece[0][1], piece[1]) for piece in pieces]

    def place_piece(self) -> None:
        """
        The place distribution of chess pieces is transformed
        into the distribution of chess pieces on the chessboard.
        """

        # If key does not exist, it returns None instead of raise an exception.
        self._data = defaultdict(lambda: None)
        for piece in self.pieces:
            for p in piece.places:
                self._data[p[:2]] = (piece.color, piece.name, p[2])

    def game_over(self) -> Winner:
        """
        Judge whether the game is over,
        and return to the winner if the game is over.
        """

        # Whether the white King exists.
        white_king = any(
            [
                piece.name == Name.KING and len(piece.places) > 0
                for piece in self.pieces
                if piece.color == Color.WHITE
            ]
        )
        # Whether the black King exists.
        black_king = any(
            [
                piece.name == Name.KING and len(piece.places) > 0
                for piece in self.pieces
                if piece.color == Color.BLACK
            ]
        )
        if white_king and black_king:
            return Winner.NULL
        elif white_king and not black_king:
            return Winner.WHITE
        elif black_king and not white_king:
            return Winner.BLACK
        else:
            return Winner.DRAW

    @staticmethod
    def transform_place(place: Any) -> Optional[Tuple[int, int]]:
        """
        Convert the place coordinates of various formats to the same format.
        """
        if place is None:
            return None

        if len(place) != 2:
            raise ValueError(f"Position format error: {place}")

        if isinstance(place, str):
            place = (ord(place[0].upper()) - ord("A") + 1, int(place[1]))

        if any([x < 1 or x > 8 for x in place]):
            raise ValueError(f"Position out of bounds: {place}")

        return place

    def __getitem__(self, key: Any) -> Optional[Tuple[Color, Name, float]]:
        """
        Get the piece at a certain place on the chessboard.
        The obtained pieces are returned in (color, name, probability) format.
        If there are no pieces in this place, return None.
        """
        return self._data[self.transform_place(key)]

    @property
    def data(self) -> defaultdict:
        """A chessboard with chess pieces."""
        return self._data

    def get_piece(self, keys: List[Tuple[int, int]]) -> Optional[Piece]:
        """
        Get the piece according to one or more positions.
        (Due to the split movement, a chess piece may be in multiple positions.)
        """
        keys = [self.transform_place(key) for key in keys]
        for piece in self.pieces:
            # Only when the pieces in all positions
            # originate from the same piece will the piece be returned.
            if all([piece.find(key) for key in keys]):
                return piece
        else:
            return None

    def select_piece(self, color: Color) -> Iterator[Tuple[int, int]]:
        """Get all the surviving pieces according to the color."""
        for piece in self.pieces:
            if piece.color != color:
                continue

            places = [place[:2] for place in piece.places]
            for place in places:
                yield (place,)

    def move_piece(
        self, source: Tuple[Tuple[int, int]], target: Tuple[Tuple[int, int]]
    ) -> "ChessBoard":
        """
        Move the piece.

        Notes
        -----
        For normal movement, there is only one source and target.
        For split movement, there is one source and two targets.
        For merge movement, there are two sources and one target.

        Parameters
        ----------
        source : tuple
            The initial place of the chess piece.
        target : tuple
            The end place of the chess piece.

        Returns
        -------
        chessboard : ChessBoard
            A new chessboard.

        """

        # Get the piece to move according to the source.
        piece = self.get_piece(source)
        # All current pieces.
        pieces = self.pieces

        # All subclasses of ActionRule constitute the rules of movement.
        for rule in ActionRule.__subclasses__():
            color = piece.color
            name = piece.name
            # If the current action matches to a rule, 
            # the action will be carried out according to 
            # the action method determined by the rule.
            if rule.condition(color, name, source, target, self.data):
                self.record = rule.action(color, name, source, target, pieces)
                # Update the chessboard after the action is completed.
                self.place_piece()
                break

        # When one side finishes playing chess, it's the other side's turn.
        self.color = Color.BLACK if self.color == Color.WHITE else Color.WHITE
        # Return self for chain call.
        return self

    def actions(self, color: Optional[Color] = None) -> list:
        """Get a list of all possible actions."""
        color = color or self.color
        data = []
        # Select one of all pieces as the source.
        for source in self.select_piece(color):
            piece = self.get_piece(source)
            if piece:
                # Determine the reachable target according to 
                # the moving rules of the piece.
                data.extend(
                    [(source, target) for target in piece.next(source, self.data)]
                )

        # Special actions such as split movement and convergence movement 
        # are combined from ordinary actions.
        for rule in SpecialMoveRule.__subclasses__():
            data = rule.transform(data, self.pieces)

        return data

    def copy(self) -> "ChessBoard":
        """
        Return a deep copy of self.
        Actions performed on the copy do not affect the original chessboard.
        """
        return copy.deepcopy(self)

    def evaluate(self, method: Optional[Evaluate] = None) -> float:
        """Evaluate the current situation."""
        method = method or eval(setting.evaluation_class)
        return method.evaluate(self._data)

    def __str__(self) -> str:
        """
        Convert the chessboard to a string. 
        Mainly used for debugging.
        """
        boundary = "  +" + "-" * 24 + "+\n"
        s = boundary
        for row in range(8, 0, -1):
            s += f"{row} |"
            for col in range(1, 8 + 1):
                piece = self._data.get((col, row), None)
                if piece is None:
                    s += " . "
                elif piece[0] == Color.WHITE:
                    name = setting.name_list[setting.print_name][piece[1].value]
                    s += f"{name.upper():^3}"
                elif piece[0] == Color.BLACK:
                    name = setting.name_list[setting.print_name][piece[1].value]
                    s += f"{name.lower():^3}"
            s += "|\n"
        s += boundary + "    a  b  c  d  e  f  g  h"
        return s

    def __repr__(self) -> str:
        """Same as `__str__`."""
        return self.__str__()

    def save(self, name: str, type_: int = 1) -> int:
        """
        Save the current chessboard to the database.

        Parameters
        ----------
        name : str
            The name of the chessboard. It can be repeated.
        type_ : int
            0 represents the system endgame, 
            and 1 represents the endgame saved by the user.

        Returns
        -------
        id : int
            The globally unique number of the archive.
            Can be used to reload the game.
        """
        data = []
        for piece in self.pieces:
            data.append(
                [(piece.color.name.lower(), piece.name.name.lower()), piece.places]
            )

        database = Database()
        return database.save(data, name, type_, self.color != Color.WHITE)
