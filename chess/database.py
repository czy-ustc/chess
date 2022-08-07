# Author       : czy
# Description  : A database object that manages the endgame.
#
# Copyright 2022 Zhiyuan Chen <chenzhiyuan@mail.ustc.edu.cn>

import json
from pathlib import Path
from typing import Union

from chess.settings import setting
from chess.orm import ON_DELETE, Model, field, sqlite, Table


class Endgame(Model):
    """Endgame."""

    id = field.IntegerField(autoincrement=True, primary_key=True)
    name = field.CharField(max_length=50)
    type_ = field.IntegerField()
    turn = field.BooleanField()


class Piece(Model):
    """Pieces in the endgame."""

    id = field.IntegerField(autoincrement=True, primary_key=True)
    eid = field.ForeignKey(to=Endgame, on_delete=ON_DELETE.CASCADE)
    color = field.CharField(max_length=5)
    name = field.CharField(max_length=10)


class Place(Model):
    """The place distribution of chess pieces."""

    id = field.IntegerField(autoincrement=True, primary_key=True)
    pid = field.ForeignKey(to=Piece, on_delete=ON_DELETE.CASCADE)
    col = field.IntegerField()
    row = field.IntegerField()
    probability = field.FloatField()


class Database:
    """
    The manager of the endgame.

    Parameters
    ----------
    filename : str
        SQLite3 database file name.
        The default value is set by the configuration file.

    """

    def __init__(self, filename: str = setting.database) -> None:
        sqlite.SqiteEngine(
            str(Path(__file__).with_name(filename).absolute()),
            check_same_thread=False,
        )

    def save(
        self, data: Union[list, str], name: str, type_: int, turn: bool = False
    ) -> int:
        """
        Save the chessboard to the database.

        Parameters
        ----------
        data : list or str
            Chessboard data.
        name : str
            The name of the chessboard. It can be repeated.
        type_ : int
            0 represents the system endgame,
            and 1 represents the endgame saved by the user.
        turn : bool
            Whose turn is it to play chess.
            False for white and True for black.

        Returns
        -------
        id : int
            The globally unique number of the archive.
            Can be used to reload the game.
        """
        if isinstance(data, str):
            data = json.loads(data)

        # Create a new endgame.
        id = Table(Endgame).insert(name=name, type_=type_, turn=turn).id

        for d in data:
            # Store the pieces in the database one by one.
            pid = Table(Piece).insert(eid=id, color=d[0][0], name=d[0][1]).id
            for p in d[1]:
                Table(Place).insert(pid=pid, col=p[0], row=p[1], probability=p[2])

        return id

    def load(self, id: int) -> list:
        """
        Reload the endgame according to the `id`.
        This `id` is the return value of `save()`.
        The returned data has been processed
        and can be directly converted to Game.
        """
        pieces = Table(Endgame).get(id).piece_set
        data = []
        for piece in pieces:
            data.append(
                [
                    [piece.color, piece.name],
                    [
                        [place.col, place.row, place.probability]
                        for place in piece.place_set
                    ],
                ]
            )
        return data

    def search(self, type_: int) -> list:
        """
        Get a list of specific types of endgame.
        0 represents the system endgame,
        and 1 represents the endgame saved by the user.
        """
        return [
            {"id": e.id, "name": e.name, "turn": e.turn}
            for e in Table(Endgame).where(type_=type_)
        ]

    def get(self, id: int) -> dict:
        """Get the basic information of the endgame according to the `id`."""
        endgame = Table(Endgame).get(id)
        return {"id": endgame.id, "name": endgame.name, "turn": endgame.turn}

    def remove(self, id: int) -> None:
        """Delete the endgame according to the id."""
        Table(Endgame).where(id=id).delete()
