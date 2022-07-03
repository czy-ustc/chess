# Author       : czy
# Description  : Integration of each module.
#
# Copyright 2022 Zhiyuan Chen <chenzhiyuan@mail.ustc.edu.cn>

from typing import Any, Dict, List, Union

from chess.agent import *
from chess.chessboard import ChessBoard
from chess.constant import Color, Winner
from chess.database import Database
from chess.game import Game


class Chess:
    """A chess game consisting of one chessboard and two players."""

    @classmethod
    def agents(cls) -> List[str]:
        return [agent.__name__.replace("Agent", "") for agent in Agent.__subclasses__()]

    @property
    def agent1(self) -> Agent:
        """Get player 1."""
        return self._agent1

    @agent1.setter
    def agent1(self, value: Union[str, dict]) -> None:
        """
        Set player 1.

        Parameters
        ----------
        value : str or dict
            If `value` is str, create an agent of the specified type,
            otherwise update the configuration.

        """
        if isinstance(value, str):
            self._agent1 = eval(f"{value}Agent")()
        else:
            self._agent1 = self._agent1.__class__(value)

    @property
    def agent2(self) -> Agent:
        """Get player 2."""
        return self._agent2

    @agent2.setter
    def agent2(self, value: Union[str, dict]) -> None:
        """
        Set player 2.

        Parameters
        ----------
        value : str or dict
            If `value` is str, create an agent of the specified type,
            otherwise update the configuration.

        """
        if isinstance(value, str):
            self._agent2 = eval(f"{value}Agent")()
        else:
            self._agent2 = self._agent2.__class__(value)

    @property
    def chessboard(self) -> ChessBoard:
        """Get the current chessboard."""
        return self._chessboard

    @chessboard.setter
    def chessboard(self, data: Union[ChessBoard, list, int]) -> None:
        """
        Set chessboard.

        Parameters
        ----------
        chessboard : ChessBoard or list or int
            Initial chessboard.
            If `chessboard` is ChessBoard, simply makes a copy of it.
            If `chessboard` is list, then it represents
            the distribution of chess pieces on the chessboard,
            and the chessboard can be initialized with this data.
            If `chessboard` is int,
            the corresponding chessboard will be loaded from the database.

        """
        # Initialize chessboard.
        if isinstance(data, ChessBoard):
            self._chessboard = data
        elif isinstance(data, list):
            if len(data) > 0:
                self._chessboard = ChessBoard(Game(data))
            else:
                self._chessboard = ChessBoard(Game())
        else:
            self._chessboard = ChessBoard(Game.load(data))
            # Since the chessboard in the database may turn to black,
            # it needs to be set.
            turn = self._database.get(data)["turn"]
            self._chessboard.color = Color.WHITE if not turn else Color.BLACK

    @property
    def database(self) -> Database:
        """Get database."""
        return self._database

    def __init__(self) -> None:
        self._chessboard = None
        self._agent1 = None
        self._agent2 = None

        self._database = Database()

        # Store chess records.
        self._records = []
        # Store the chessboard of each step to undo the previous step.
        self._stack = []

    def actions(self) -> list:
        """
        Get the list of possible actions on the current chessboard.

        Returns
        -------
        actions : list
            Actions list. Each action consists of a source and a target,
            such as (((1, 2),), ((1, 4),)).

        """
        return self._chessboard.actions()

    def run(self, *args: Any) -> str:
        """
        Perform one step.

        Parameters
        ----------
        args : any
            Parameters passed to the agent.
            Usually, only HumanAgent needs to pass parameters.

        """

        # Record the current chessboard before playing chess.
        self._stack.append(self._chessboard.copy())

        # Select agent.
        if self._chessboard.color == Color.WHITE:
            agent = self._agent1
        else:
            agent = self._agent2

        # Perform actions.
        record = agent.run(self._chessboard, *args)

        # Log.
        self._records.append(record)
        return record

    def undo(self) -> None:
        """Undo the previous step."""
        self._chessboard = self._stack.pop()

    def save(self, name: str) -> int:
        """
        Save the current chessboard to the database.

        Parameters
        ----------
        name : str
            The name of the chessboard. It can be repeated.

        Returns
        -------
        id : int
            The globally unique number of the archive.
            Can be used to reload the game.

        """
        return self._chessboard.save(name, 1)

    def end(self) -> None:
        """End the current game."""
        self._chessboard = None
        self._records = []
        self._stack = []

    @property
    def data(self) -> dict:
        """
        JSON format chessboard.

        Notes
        -----
        It is usually used to transmit data to the front end.

        Returns
        -------
        data : dict
            The key represents a grid (in the format of (column, row)),
            and the value is an array with three elements,
            represent the color, name and probability
            of the chess pieces respectively.

        Examples
        --------
        >>> chess.data
        {'12': ['white', 'pawn', 1], '41': ['white', 'king', 0.5], '58': ['black', 'king', 1]}

        """
        d = {}
        for i in range(1, 8 + 1):
            for j in range(1, 8 + 1):
                piece = self._chessboard[(i, j)]
                if piece is not None:
                    color, name, probability = piece
                    color = color.name.lower()
                    name = name.name.lower()
                    d[f"{i}{j}"] = [color, name, probability]
        return d

    @property
    def dead(self) -> Dict[str, List[str]]:
        """
        All pieces that have been removed from the chessboard currently.

        Returns
        -------
        dead : dict
            The key represents color (white or black),
            and the value is the pieces that have been removed.

        Examples
        --------
        >>> chess.dead
        {'white': ['pawn', 'pawn'], 'black': ['knight']}

        """

        # List of all pieces.
        tomb = {
            "white": [
                "pawn",
                "pawn",
                "pawn",
                "pawn",
                "pawn",
                "pawn",
                "pawn",
                "pawn",
                "rook",
                "knight",
                "bishop",
                "queen",
                "king",
                "bishop",
                "knight",
                "rook",
            ],
            "black": [
                "pawn",
                "pawn",
                "pawn",
                "pawn",
                "pawn",
                "pawn",
                "pawn",
                "pawn",
                "rook",
                "knight",
                "bishop",
                "queen",
                "king",
                "bishop",
                "knight",
                "rook",
            ],
        }

        # If the piece exists on the chessboard,
        # remove it from the tomb list.
        for piece in self._chessboard.pieces:
            for place in piece.places:
                if place[2] != 0:
                    break
            else:
                continue

            # Due to the rules of `Pawn Promotion`,
            # there may be multiple queens/knights/bishops/knights.
            try:
                if piece.color == Color.WHITE:
                    tomb["white"].remove(piece.name.name.lower())
                else:
                    tomb["black"].remove(piece.name.name.lower())
            except ValueError:
                if piece.color == Color.WHITE:
                    tomb["white"].remove("pawn")
                else:
                    tomb["black"].remove("pawn")

        return tomb

    @property
    def winner(self) -> Winner:
        """
        The winner of the game (Winner.WHITE or Winner.BLACK).
        If the game is not over yet, Winner.NULL will be returned.

        """
        return self._chessboard.game_over()
