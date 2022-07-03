# Author       : czy
# Description  : A database object that manages the endgame.
#
# Copyright 2022 Zhiyuan Chen <chenzhiyuan@mail.ustc.edu.cn>

import json
from pathlib import Path
from sqlite3 import Connection as SQLite3Connection
from typing import Union

from sqlalchemy import (
    Boolean,
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
    create_engine,
    event,
)
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.pool import SingletonThreadPool

from chess.settings import setting


@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    """Open foreign key check."""
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()


Base = declarative_base()


class Endgame(Base):
    """Endgame."""

    __tablename__ = "endgame"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    type_ = Column(Integer)
    turn = Column(Boolean)
    piece = relationship("Piece", backref="piece", passive_deletes=True)


class Piece(Base):
    """Pieces in the endgame."""

    __tablename__ = "piece"

    id = Column(Integer, primary_key=True, autoincrement=True)
    eid = Column(Integer, ForeignKey("endgame.id", ondelete="CASCADE"))
    color = Column(String(5))
    name = Column((String(10)))
    place = relationship("Place", backref="place", passive_deletes=True)


class Place(Base):
    """The place distribution of chess pieces."""

    __tablename__ = "place"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pid = Column(Integer, ForeignKey("piece.id", ondelete="CASCADE"))
    col = Column(Integer)
    row = Column(Integer)
    probability = Column(Float)


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
        filepath = Path(__file__).with_name(filename).absolute()
        flag = filepath.exists()
        self.engine = create_engine(
            f"sqlite:///{filepath}",
            poolclass=SingletonThreadPool,
            connect_args={"check_same_thread": False},
        )
        DbSession = sessionmaker(bind=self.engine)
        self.session = DbSession()

        if not flag:
            self.create()

    def create(self) -> None:
        """Create tables."""
        Base.metadata.create_all(self.engine, checkfirst=True)

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
        session = self.session

        if isinstance(data, str):
            data = json.loads(data)

        # Create a new endgame.
        endgame = Endgame(name=name, type_=type_, turn=turn)
        session.add(endgame)
        session.flush()
        id = endgame.id

        for d in data:
            # Store the pieces in the database one by one.
            piece = Piece(eid=id, color=d[0][0], name=d[0][1])
            session.add(piece)
            session.flush()
            pid = piece.id
            for p in d[1]:
                place = Place(pid=pid, col=p[0], row=p[1], probability=p[2])
                session.add(place)

        session.commit()
        return id

    def load(self, id: int) -> list:
        """
        Reload the endgame according to the `id`.
        This `id` is the return value of `save()`.
        The returned data has been processed
        and can be directly converted to Game.
        """
        session = self.session

        pieces = session.query(Piece).filter_by(eid=id).all()
        data = []
        for piece in pieces:
            places = session.query(Place).filter_by(pid=piece.id).all()
            data.append(
                [
                    [piece.color, piece.name],
                    [[place.col, place.row, place.probability] for place in places],
                ]
            )
        return data

    def search(self, type_: int) -> list:
        """
        Get a list of specific types of endgame.
        0 represents the system endgame,
        and 1 represents the endgame saved by the user.
        """
        session = self.session
        endgames = session.query(Endgame).filter_by(type_=type_)
        return [{"id": e.id, "name": e.name, "turn": e.turn} for e in endgames]

    def get(self, id: int) -> dict:
        """Get the basic information of the endgame according to the `id`."""
        session = self.session
        endgame = session.query(Endgame).filter_by(id=id).first()
        return {"id": endgame.id, "name": endgame.name, "turn": endgame.turn}

    def remove(self, id: int) -> None:
        """Delete the endgame according to the id."""
        session = self.session

        pieces = session.query(Piece).filter_by(eid=id).all()
        for piece in pieces:
            session.query(Place).filter_by(pid=piece.id).delete()

        session.query(Piece).filter_by(eid=id).delete()
        session.query(Endgame).filter_by(id=id).delete()
        session.commit()
