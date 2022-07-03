# Author       : czy
# Description  : Quantum chess piece,
#                may appear in multiple positions at the same time.
#
# Copyright 2022 Zhiyuan Chen <chenzhiyuan@mail.ustc.edu.cn>

import random
from collections import defaultdict
from typing import Iterator, List, Optional, Tuple

from chess.constant import Color, Name
from chess.rule import *
from chess.settings import setting


class Piece:
    """
    Quantum chess piece.

    Parameters
    ----------
    color : Color
        The color of the piece.
    name : Name
        The name of the piece.
    places : list of tuple
        Where the chess pieces may exist.
        Each place consists of three values.
        The first two represent the column and row (from 1 to 8),
        and the last represents the probability of the chess piece
        appearing in this place.

    """

    def __init__(
        self,
        color: Color,
        name: Name,
        places: List[Tuple[int, int, float]],
    ) -> None:

        self.color = color
        self.name = name
        self.places = places

        # Different types of pieces have different moving rules.
        self.rule = eval(f"{setting.rules[self.name.value]}()")

    def __str__(self) -> str:
        """
        Convert to string.
        Mainly for debugging.
        """
        name = setting.name_list[setting.display_name][self.name.value]
        return f"{self.color.name}<{name}>{self.places}"

    def __repr__(self) -> str:
        """Same as `__str__()`."""
        return self.__str__()

    def add(self, place: Tuple[int, int, float]) -> None:
        """Add a possible place."""
        self.places.append(place)

    def remove(self, place: Tuple[int, int]) -> Optional[Tuple[int, int, float]]:
        """Delete and return to a possible place."""
        for p in self.places:
            if p[:2] == place:
                val = p
                self.places.remove(p)
                return val
        else:
            return None

    def clear(self) -> None:
        """
        Empty all possible positions.
        In fact, it means that the chess piece has been eaten.
        """
        self.places = []

    def find(self, place: Tuple[int, int]) -> bool:
        """Judge whether the piece may appear in a certain place."""
        return any([p[:2] == place for p in self.places])

    def get(self, place: Tuple[int, int]) -> float:
        """Get the probability that the piece appears in a certain place."""
        for p in self.places:
            if p[:2] == place:
                return p[2]
        else:
            return 0

    def next(
        self, selected: List[Tuple[int, int]], data: defaultdict
    ) -> Iterator[Tuple]:
        """
        Generate the next possible action according to the type of the piece.
        The generation method is specified by `self.rule`.
        """
        for step in self.rule.next(self.color, selected, data):
            yield (step,)

    def measure(self) -> Optional[Tuple[int, int]]:
        """
        Measure the piece.

        Notes
        -----
        Like standard quantum mechanics, 
        measurement will cause the superposition state 
        to collapse to a certain state, 
        which means that the state of the chess piece 
        will change after measurement.

        Returns
        -------
        place : tuple, optional
            The place of the chess piece after measurement.
            If a part of the piece has been eaten by the other party 
            before the measurement, 
            the piece may not exist after the measurement.

        """
        probability = random.random()
        random.shuffle(self.places)
        for place in self.places:
            probability -= place[2]
            if probability < 1e-6:
                self.places = [(place[0], place[1], 1)]
                return (place[0], place[1])

        return None

    def superposed(self) -> bool:
        """Judge whether the piece can appear in multiple positions."""
        return not (len(self.places) == 1 and self.places[0][2] == 1)
