# Author       : czy
# Description  : All the rules of quantum chess.
#
# Copyright 2022 Zhiyuan Chen <chenzhiyuan@mail.ustc.edu.cn>

from collections import defaultdict
from itertools import combinations
from typing import Iterator, List, Optional, Tuple

from chess.constant import Color, Name, State


class Rule:
    """Base class for all rule classes."""

    @staticmethod
    def overstep(place: Tuple[int, int]) -> bool:
        """Judge whether the piece cross the boundary."""
        return not all(map(lambda x: 1 <= x <= 8, place))

    @classmethod
    def find(cls, place: Tuple[int, int], pieces: list):
        """
        Find the pieces that may appear
        in the specified place in the list of pieces.
        """
        for piece in pieces:
            if piece.find(place):
                return piece
        else:
            return None


class MoveRule(Rule):
    """
    Base class for all move rule classes.
    Its subclasses stipulate the moving rules of all kinds of pieces.
    """

    # List of possible moves.
    moves = []

    @classmethod
    def check(
        cls,
        color: Color,
        cur: Tuple[int, int],
        next: Tuple[int, int],
        piece: Optional[Tuple[Color, Name, float]],
    ) -> State:
        """
        Check whether a specific movement is legal.

        Parameters
        ----------
        color : Color
            The color of the current player.
        cur : tuple
            The current place of the piece.
        next : tuple
            The next place of the piece.
        piece : tuple, optional
            Piece in the next place.
            (There may be no pieces in this place.)

        Returns
        -------
        state : State
            The status of the action.
            `State.UNOCCUPIED` means there are no pieces in this place.
            `State.REACHABLE` means that this place can be reached,
            but the next place cannot be reached.
            For example, this piece is the opponent's
            (you can eat this chess piece but cannot reach the next place).
            `State.UNREACHABLE` means that this place
            and its subsequent positions cannot be reached.
            ``

        """

        # No obstacles or cccupy the space in superposition state
        if piece is None or 1 - piece[2] > 1e-6:
            return State.UNOCCUPIED

        # Eat the opponent's chess pieces
        if piece[0] != color:
            return State.REACHABLE
        # Can't eat one's own chess pieces
        else:
            return State.UNREACHABLE

    @classmethod
    def next(
        cls, color: Color, selected: List[Tuple[int, int]], data: defaultdict
    ) -> Iterator[Tuple[int, int]]:
        """
        Generate the possible place of the next step according to `moves`.

        Parameters
        ----------
        color : Color
            The color of the current player.
        selected : list of tuple
            Selected place.
        data : defaultdict
            Chessboard data.

        Returns
        -------
        place : tuple
            Next possible place.

        """
        selected = selected[0]

        for move in cls.moves:
            for step in move:
                next = (selected[0] + step[0], selected[1] + step[1])
                # If it crosses the boundary, the place will be discarded.
                if Rule.overstep(next):
                    break

                # Check whether the place is legal.
                piece = data[next]
                state = cls.check(color, selected, next, piece)

                if state == State.UNOCCUPIED:
                    yield next
                elif state == State.REACHABLE:
                    yield next
                    break
                else:
                    break


class PawnMoveRule(MoveRule):
    """The movement rules of pawn."""

    moves = [
        # White:
        # Forward
        [(0, 1)],
        [(0, 2)],
        # Pass by
        [(1, 1)],
        [(-1, 1)],
        # Black:
        # Forward
        [(0, -1)],
        [(0, -2)],
        # Pass by
        [(1, -1)],
        [(-1, -1)],
    ]

    @classmethod
    def check(
        cls,
        color: Color,
        cur: Tuple[int, int],
        next: Tuple[int, int],
        piece: Optional[Tuple[Color, Name, float]],
    ) -> State:
        # Can only move forward, not backward
        if color == Color.WHITE and cur[1] > next[1]:
            return State.UNREACHABLE
        elif color == Color.BLACK and cur[1] < next[1]:
            return State.UNREACHABLE

        # Only the first action can move two spaces
        if abs(cur[1] - next[1]) == 2 and not (
            (color == Color.WHITE and cur[1] == 2)
            or (color == Color.BLACK and cur[1] == 7)
        ):
            return State.UNREACHABLE

        if cur[0] == next[0]:
            # No obstacles or cccupy the space in superposition state
            if not (piece is None or 1 - piece[2] > 1e-6):
                return State.UNREACHABLE
        else:
            # Can only eat the opponent's chess pieces
            if piece is None or piece[0] == color:
                return State.UNREACHABLE

        return State.REACHABLE


class RookMoveRule(MoveRule):
    """The movement rules of rook."""

    moves = [
        # Right
        list(zip(range(1, 8), [0] * 7)),
        # Left
        list(zip(range(-1, -8, -1), [0] * 7)),
        # Font
        list(zip([0] * 7, range(1, 8))),
        # Back
        list(zip([0] * 7, range(-1, -8, -1))),
    ]

    @classmethod
    def check(
        cls,
        color: Color,
        cur: Tuple[int, int],
        next: Tuple[int, int],
        piece: Optional[Tuple[Color, Name, float]],
    ) -> State:
        state = MoveRule.check(color, cur, next, piece)
        # Castling
        if (
            piece
            and state == State.UNREACHABLE
            and piece[0] == color
            and piece[1] == Name.KING
            and piece[2] == 1
            and next[0] == 5
            and (cur[0] == 1 or cur[0] == 8)
            and cur[1] == (1 if color == Color.WHITE else 8)
        ):
            return State.REACHABLE
        else:
            return state


class KnightMoveRule(MoveRule):
    """The movement rules of knight."""

    moves = [
        # Upper right
        [(1, 2)],
        [(2, 1)],
        # Upper left
        [(-1, 2)],
        [(-2, 1)],
        # Lower right
        [(1, -2)],
        [(2, -1)],
        # Lower left
        [(-1, -2)],
        [(-2, -1)],
    ]

    @classmethod
    def check(
        cls,
        color: Color,
        cur: Tuple[int, int],
        next: Tuple[int, int],
        piece: Optional[Tuple[Color, Name, float]],
    ) -> State:
        # If the place is occupied by one's own chess pieces, can't reach it
        if piece and piece[0] == color and piece[2] == 1:
            return State.UNREACHABLE
        return State.REACHABLE


class BishopMoveRule(MoveRule):
    """The movement rules of bishop."""

    moves = [
        # Upper right
        list(zip(range(1, 8), range(1, 8))),
        # Upper left
        list(zip(range(-1, -8, -1), range(1, 8))),
        # Lower right
        list(zip(range(1, 8), range(-1, -8, -1))),
        # Lower left
        list(zip(range(-1, -8, -1), range(-1, -8, -1))),
    ]


class QueenMoveRule(MoveRule):
    """The movement rules of queen."""

    moves = [
        # Right
        list(zip(range(1, 8), [0] * 7)),
        # Left
        list(zip(range(-1, -8, -1), [0] * 7)),
        # Font
        list(zip([0] * 7, range(1, 8))),
        # Back
        list(zip([0] * 7, range(-1, -8, -1))),
        # Upper right
        list(zip(range(1, 8), range(1, 8))),
        # Upper left
        list(zip(range(-1, -8, -1), range(1, 8))),
        # Lower right
        list(zip(range(1, 8), range(-1, -8, -1))),
        # Lower left
        list(zip(range(-1, -8, -1), range(-1, -8, -1))),
    ]


class KingMoveRule(MoveRule):
    """The movement rules of king."""

    moves = [
        # Go straight or diagonally, one space per step
        [(1, 1)],
        [(1, 0)],
        [(1, -1)],
        [(0, 1)],
        [(0, -1)],
        [(-1, 1)],
        [(-1, 0)],
        [(-1, -1)],
    ]


class SpecialMoveRule(Rule):
    """
    SpecialMoveRule describes special movements
    with multiple sources or targets.
    """

    @classmethod
    def transform(cls, actions: list, pieces: list) -> list:
        """
        Combine the basic movements to get new special movements.

        Parameters
        ----------
        actions : list
            List of possible actions.
        pieces : list
            Chess list.

        Returns
        -------
        actions : list
            New action list.

        """
        return NotImplemented


class SplitMove(SpecialMoveRule):
    """Split movement."""

    @classmethod
    def transform(cls, actions: list, pieces: list) -> list:
        src_dict = {}
        for source, target in actions:
            # It only works on ordinary movements
            # with only one source and one target
            if len(source) > 1 or len(target) > 1:
                continue

            # Pawn can't split move
            src_piece = cls.find(source[0], pieces)
            if src_piece.name == Name.PAWN:
                continue

            if source[0] not in src_dict:
                src_dict[source[0]] = []

            dst_piece = cls.find(target[0], pieces)
            # Can only split to space unoccupied or occupied by similar pieces
            if (not dst_piece) or (
                dst_piece.color == src_piece.color and dst_piece.name == src_piece.name
            ):
                src_dict[source[0]].append(target[0])

        for source, targets in src_dict.items():
            # Combine possible targets.
            for dst1, dst2 in combinations(targets, 2):
                if dst1 != dst2:
                    actions.append(((source,), (dst1, dst2)))

        return actions


class MergeMove(SpecialMoveRule):
    """Merge movement."""

    @classmethod
    def transform(cls, actions: list, pieces: list) -> list:
        dst_dict = {}
        for source, target in actions:
            # It only works on ordinary movements
            # with only one source and one target
            if len(source) > 1 or len(target) > 1:
                continue

            if target[0] not in dst_dict:
                dst_dict[target[0]] = []

            dst_dict[target[0]].append(source[0])

        # Can only be merged into space unoccupied
        for target, sources in dst_dict.items():
            dst_piece = cls.find(target, pieces)
            # Combine possible targets.
            for src1, src2 in combinations(sources, 2):
                # Only homologous pieces can be merged
                src_piece = cls.find(src1, pieces)
                if src_piece.find(src2) and dst_piece is None and src1 != src2:
                    actions.append(((src1, src2), (target,)))

        return actions


class ActionRule(Rule):
    """
    Base class for all action rule classes.
    Its subclasses specify how to deal with a specific action
    from source to target.
    """

    @classmethod
    def place2str(cls, place: Tuple[int, int]) -> str:
        """Converts the place to a string for logging."""
        return f"{chr(ord('a') + place[0] - 1)}{place[1]}"

    @classmethod
    def piece2str(cls, piece: object) -> str:
        """Converts the piece to a string for logging."""
        mapping = {
            Name.KING: "K",
            Name.QUEEN: "Q",
            Name.ROOK: "R",
            Name.BISHOP: "B",
            Name.KNIGHT: "N",
            Name.PAWN: "",
        }
        return mapping[piece.name]

    @classmethod
    def obstacle(
        cls, source: Tuple[int, int], target: Tuple[int, int], pieces: list
    ) -> float:
        """
        Calculate the probability of encountering obstacles on the way
        from the source to the target.
        """
        vec = (target[0] - source[0], target[1] - source[1])
        # The knight will not encounter obstacles
        if vec[0] != 0 and vec[1] != 0 and abs(vec[0]) != abs(vec[1]):
            return 0

        stepX = 0 if vec[0] == 0 else (vec[0] // abs(vec[0]))
        stepY = 0 if vec[1] == 0 else (vec[1] // abs(vec[1]))

        x = source[0] + stepX
        y = source[1] + stepY

        while x != target[0] or y != target[1]:
            for piece in pieces:
                # If there is piece in superposition state on the road,
                #  its probability is returned.
                p = piece.get((x, y))
                if p > 0:
                    return p

            x += stepX
            y += stepY

        return 0

    @classmethod
    def condition(
        cls,
        color: Color,
        name: Name,
        source: Tuple[Tuple[int, int]],
        target: Tuple[Tuple[int, int]],
        data: defaultdict,
    ) -> bool:
        """
        Judge whether the action from source to target
        matches to the action rule.

        Parameters
        ----------
        color : Color
            The color of the piece.
        name : Name
            The name of the piece.
        source : tuple
            Location of the source.
        target : tuple
            Location of the target.
        data : defaultdict
            Chessboard data.

        Returns
        -------
        flag : bool
            Returns true if it matches, False otherwise.

        """
        return NotImplemented

    @classmethod
    def action(
        cls,
        color: Color,
        name: Name,
        source: Tuple[Tuple[int, int]],
        target: Tuple[Tuple[int, int]],
        pieces: list,
    ) -> str:
        """
        For the matching action, the pieces are processed.

        Parameters
        ----------
        color : Color
            The color of the piece.
        name : Name
            The name of the piece.
        source : tuple
            Location of the source.
        target : tuple
            Location of the target.
        pieces : list
            Pieces list.

        Returns
        -------
        record : str
            Record of action,
            such as `Nb1-a3` (Knight moves from (2, 1) to (1, 3)).

        """
        return NotImplemented


class MoveActionRule(ActionRule):
    """Action rule for simple mobile action."""

    @classmethod
    def condition(
        cls,
        color: Color,
        name: Name,
        source: Tuple[Tuple[int, int]],
        target: Tuple[Tuple[int, int]],
        data: defaultdict,
    ) -> bool:
        # There can only be one source and one target,
        # and there can be no piece at the target place.
        return len(source) == 1 and len(target) == 1 and data[target[0]] is None

    @classmethod
    def action(
        cls,
        color: Color,
        name: Name,
        source: Tuple[Tuple[int, int]],
        target: Tuple[Tuple[int, int]],
        pieces: list,
    ) -> str:
        # Pawn promotion: Default to queen.
        promotion = name == Name.PAWN and target[0][1] == (
            8 if color == Color.WHITE else 1
        )

        piece = cls.find(source[0], pieces)
        if promotion:
            # promot success.
            if piece.measure() == source[0]:
                piece.clear()
                piece.add((*target[0], 1))
                piece.name = Name.QUEEN

            return cls.place2str(target[0]) + "-Q"

        # The moving record is like `a-b`.
        record = "-".join([cls.place2str(source[0]), cls.place2str(target[0])])
        record = cls.piece2str(piece) + record

        probability = piece.remove(source[0])[2]
        if probability < 1:
            piece.add((*target[0], probability))
        # Determine whether there are obstacles on the road.
        else:
            value = cls.obstacle(source[0], target[0], pieces)
            # Enter the superposition state when there are obstacles.
            if value > 0:
                piece.add((*target[0], value))
                piece.add((*source[0], 1 - value))
            else:
                piece.add((*target[0], probability))

        return record


class AttackActionRule(ActionRule):
    """Action rule for eating piece."""

    @classmethod
    def condition(
        cls,
        color: Color,
        name: Name,
        source: Tuple[Tuple[int, int]],
        target: Tuple[Tuple[int, int]],
        data: defaultdict,
    ) -> bool:
        piece = data[target[0]]
        # There is only one source and one target,
        # and there is opposing piece at the target place.
        return len(source) == 1 and len(target) == 1 and piece and piece[0] != color

    @classmethod
    def action(
        cls,
        color: Color,
        name: Name,
        source: Tuple[Tuple[int, int]],
        target: Tuple[Tuple[int, int]],
        pieces: list,
    ) -> str:
        # Measure before attacking the other party.
        piece = cls.find(source[0], pieces)
        place = piece.measure()

        # The attacking record is like `axb`.
        record = "x".join([cls.place2str(source[0]), cls.place2str(target[0])])
        record = cls.piece2str(piece) + record

        # Do nothing if the measurement fails
        if place != source[0]:
            return record

        # If the measurement is successful, move to the new place
        cls.find(target[0], pieces).remove(target[0])

        piece.clear()
        piece.add((*target[0], 1))

        return record


class CastlingActionRule(ActionRule):
    """Action rule for castling."""

    @classmethod
    def condition(
        cls,
        color: Color,
        name: Name,
        source: Tuple[Tuple[int, int]],
        target: Tuple[Tuple[int, int]],
        data: defaultdict,
    ) -> bool:
        piece = data[target[0]]
        return (
            # There can only be one source and one target.
            len(source) == 1
            and len(target) == 1
            # The source must be a rook in its initial position.
            and name == Name.ROOK
            # The target must be a king in its initial position.
            and piece
            and piece[0] == color
            and piece[1] == Name.KING
            # No castling in case of separation
            and piece[2] == 1
        )

    @classmethod
    def action(
        cls,
        color: Color,
        name: Name,
        source: Tuple[Tuple[int, int]],
        target: Tuple[Tuple[int, int]],
        pieces: list,
    ) -> str:
        # Long castling.
        if source[0][0] == 1:
            rook, king = 4, 3
            record = "0-0-0"
        # Short castling.
        else:
            rook, king = 6, 7
            record = "0-0"

        # Rook moves to new place.
        piece = cls.find(source[0], pieces)
        probability = piece.remove(source[0])[2]
        piece.add((rook, source[0][1], probability))

        # King moves to new place.
        piece = cls.find(target[0], pieces)
        probability = piece.remove(target[0])[2]
        piece.add((king, target[0][1], probability))

        return record


class MeetActionRule(ActionRule):
    """
    Action rule for meeting pieces of the same color.

    Notes
    -----
    This situation is only possible when considering quantum effects.

    """

    @classmethod
    def condition(
        cls,
        color: Color,
        name: Name,
        source: Tuple[Tuple[int, int]],
        target: Tuple[Tuple[int, int]],
        data: defaultdict,
    ) -> bool:
        piece = data[target[0]]
        return (
            # There can only be one source and one target.
            len(source) == 1
            and len(target) == 1
            # There are piece of the same color at the target place.
            and piece
            and piece[0] == color
            # It's not castling.
            and (piece[2] < 1 or piece[1] != Name.KING)
        )

    @classmethod
    def action(
        cls,
        color: Color,
        name: Name,
        source: Tuple[Tuple[int, int]],
        target: Tuple[Tuple[int, int]],
        pieces: list,
    ) -> str:
        src_piece = cls.find(source[0], pieces)
        dst_piece = cls.find(target[0], pieces)

        record = "-".join([cls.place2str(source[0]), cls.place2str(target[0])])
        record = cls.piece2str(src_piece) + record

        # Exchange probability if it is a chess piece of the same kind
        if src_piece.name == dst_piece.name:
            probability1 = src_piece.remove(source[0])[2]
            probability2 = dst_piece.remove(target[0])[2]
            src_piece.add((*target[0], probability1))
            dst_piece.add((*source[0], probability2))
            return record

        dst_place = dst_piece.measure()
        # In non superposition state
        if not src_piece.superposed():
            if dst_place != target[0]:
                src_piece.clear()
                src_piece.add((*target[0], 1))
        # In superposition state
        else:
            src_place = src_piece.measure()
            # Target place is empty
            if dst_place != target[0] and src_place == source[0]:
                src_piece.clear()
                src_piece.add((*target[0], 1))

        return record


class SplitMoveActionRule(ActionRule):
    """Action rule for split movement."""

    @classmethod
    def condition(
        cls,
        color: Color,
        name: Name,
        source: Tuple[Tuple[int, int]],
        target: Tuple[Tuple[int, int]],
        data: defaultdict,
    ) -> bool:
        # There are two targets for split movement.
        return len(target) == 2

    @classmethod
    def action(
        cls,
        color: Color,
        name: Name,
        source: Tuple[Tuple[int, int]],
        target: Tuple[Tuple[int, int]],
        pieces: list,
    ) -> str:
        dst_piece0 = cls.find(target[0], pieces)
        dst_piece1 = cls.find(target[1], pieces)
        src_piece = cls.find(source[0], pieces)

        # In the record, two targets are connected through `^`
        record = f"{cls.piece2str(src_piece)}{cls.place2str(source[0])}-{cls.place2str(target[0])}^{cls.place2str(target[1])}"

        # Exchange probability with the first target
        # Then exchange probability with the second target
        if dst_piece0 and dst_piece1:
            probability1 = src_piece.remove(source[0])[2]
            probability2 = dst_piece0.remove(target[0])[2]
            probability3 = dst_piece1.remove(target[1])[2]
            src_piece.add((*target[0], probability1))
            dst_piece0.add((*target[1], probability2))
            dst_piece1.add((*source[0], probability3))

            return record

        # If there are chess pieces at the target, the probability is exchanged.
        if dst_piece0:
            dst_piece0.add((*source[0], dst_piece0.remove(target[0])[2]))
        if dst_piece1:
            dst_piece1.add((*source[0], dst_piece1.remove(target[1])[2]))

        # Split into two pieces,
        # and the probability of each piece is half of the original.
        probability = src_piece.remove(source[0])[2]
        src_piece.add((*target[0], probability / 2))
        src_piece.add((*target[1], probability / 2))

        return record


class MergeMoveActionRule(ActionRule):
    """Action rule for merge movement."""

    @classmethod
    def condition(
        cls,
        color: Color,
        name: Name,
        source: Tuple[Tuple[int, int]],
        target: Tuple[Tuple[int, int]],
        data: defaultdict,
    ) -> bool:
        # There are two sources for merge movement.
        return len(source) == 2

    @classmethod
    def action(
        cls,
        color: Color,
        name: Name,
        source: Tuple[Tuple[int, int]],
        target: Tuple[Tuple[int, int]],
        pieces: list,
    ) -> str:
        src_piece = cls.find(source[0], pieces)

        # In the record, two sources are connected through `^`
        record = f"{cls.piece2str(src_piece)}{cls.place2str(source[0])}^{cls.place2str(source[1])}-{cls.place2str(target[0])}"

        # Two pieces are combined into one,
        # and the probability is the sum of
        # the probabilities of the original two pieces.
        probability = src_piece.remove(source[0])[2] + src_piece.remove(source[1])[2]
        src_piece.add((*target[0], probability))
        return record
