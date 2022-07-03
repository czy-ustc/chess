# Author       : czy
# Description  : Agents implemented by different algorithms.
#
# Copyright 2022 Zhiyuan Chen <chenzhiyuan@mail.ustc.edu.cn>

import abc
import random
from collections import OrderedDict
from typing import Callable, List, Optional, Tuple, Union

from chess.chessboard import ChessBoard
from chess.constant import Color
from chess.evaluate import *
from chess.settings import setting


class Agent(metaclass=abc.ABCMeta):
    """Base classes for all agents."""

    @abc.abstractmethod
    def config(self) -> dict:
        """Return configuration information."""
        pass

    @abc.abstractmethod
    def run(self, chessboard: ChessBoard) -> str:
        """
        Perform one step.

        Notes
        -----
        This method will change the chessboard in place.

        Parameters
        ----------
        chessboard : ChessBoard

        Returns
        -------
        record : str
            Chess record. (Basically follow the standard chess record format.)

        """
        pass


class RandomAgent(Agent):
    """Agent with random action."""

    def __init__(self) -> None:
        super().__init__()

    def config(self) -> dict:
        return {}

    def run(self, chessboard: ChessBoard) -> str:
        """Randomly select a feasible action to execute."""
        action = random.choice(chessboard.actions())
        chessboard.move_piece(*action)
        return chessboard.record


class GreedyAgent(Agent):
    """
    Agent with greedy algorithm.

    Parameters
    ----------
    evaluate : str, optional
        Value evaluation function.

    """

    def __init__(self, evaluate: Optional[str] = None) -> None:
        super().__init__()
        self.evaluate = eval(evaluate or setting.greedy["evaluate"])

    def config(self) -> dict:
        data = setting.greedy
        data["evaluate"] = self.evaluate.__name__
        return data

    def run(self, chessboard: ChessBoard) -> str:
        # Sort actions by value
        actions = []
        for source, target in chessboard.actions():
            val = chessboard.copy().move_piece(source, target).evaluate(self.evaluate)
            actions.append((val, source, target))
        actions.sort()

        # The white side should maximize the value
        # and the black side should minimize the value
        if chessboard.color == Color.WHITE:
            extremum = actions[-1][0]
        else:
            extremum = actions[0][0]

        # In order to increase the randomness as much as possible,
        # when there are multiple actions of the same value to choose from,
        # choose one of them at random
        action = random.choice(
            [action for action in actions if abs(action[0] - extremum) < 1e-6]
        )
        chessboard.move_piece(*action[1:])
        return chessboard.record


class MinimaxAgent(Agent):
    """
    Agent with minimax algorithm.

    Parameters
    ----------
    evaluate : str, optional
        Value evaluation function.
    deepth : int, optional
        The maximum depth, beyond which the action sequence will be truncated.

    """

    def __init__(
        self, evaluate: Optional[str] = None, deepth: Optional[int] = None
    ) -> None:
        super().__init__()
        self.evaluate = eval(evaluate or setting.minimax["evaluate"])
        self.deepth = deepth or setting.minimax["deepth"]

    def config(self) -> dict:
        data = setting.minimax
        data["evaluate"] = self.evaluate.__name__
        data["deepth"] = self.deepth
        return data

    def minimax(self, deepth: int, chessboard: ChessBoard) -> List[float]:
        """
        Minimax algorithm.

        Parameters
        ----------
        deepth : int
            Remaining maximum depth (for recursive calls).
        chessboard : ChessBoard
            Current chessboard (a copy of the original chessboard).

        """
        # Constantly maximize the minimum value (for white)
        # or minimize the maximum value (for black)
        if deepth > 0:
            values = []
            for source, target in chessboard.actions():
                new_chessboard = chessboard.copy().move_piece(source, target)
                if chessboard.color == Color.WHITE:
                    value = min(self.minimax(deepth - 1, new_chessboard))
                else:
                    value = max(self.minimax(deepth - 1, new_chessboard))
                values.append(value)

        # For the last layer, return directly to the value of action
        else:
            values = [
                chessboard.copy().move_piece(source, target).evaluate(self.evaluate)
                for source, target in chessboard.actions()
            ]

        # According to the rules of chess,
        # if there is no alternative action,
        # it will be judged negative directly
        if len(values) == 0:
            if chessboard.color == Color.WHITE:
                values.append(-float("inf"))
            else:
                values.append(float("inf"))

        return values

    def run(self, chessboard: ChessBoard) -> str:
        # Calculate the value of each action
        values = self.minimax(self.deepth, chessboard)

        # Sort and choose the best action
        actions = sorted(
            [
                (values[index], *action)
                for index, action in enumerate(chessboard.actions())
            ]
        )
        if chessboard.color == Color.WHITE:
            extremum = actions[-1][0]
        else:
            extremum = actions[0][0]

        if extremum != float("inf") and extremum != -float("inf"):
            actions = [action for action in actions if abs(action[0] - extremum) < 1e-6]

        action = random.choice(actions)
        chessboard.move_piece(*action[1:])
        return chessboard.record


class AlphaBetaAgent(Agent):
    """
    Agent with alpha-beta search algorithm.

    Parameters
    ----------
    evaluate : str, optional
        Value evaluation function.
    deepth : int, optional
        The maximum depth, beyond which the action sequence will be truncated.

    """

    def __init__(
        self, evaluate: Optional[str] = None, deepth: Optional[int] = None
    ) -> None:
        super().__init__()
        self.evaluate = eval(evaluate or setting.alphabeta["evaluate"])
        self.deepth = deepth or setting.alphabeta["deepth"]

    def config(self) -> dict:
        data = setting.alphabeta
        data["evaluate"] = self.evaluate.__name__
        data["deepth"] = self.deepth
        return data

    def run(self, chessboard: ChessBoard) -> str:
        """
        Alpha-Beta search algorithm is essentially minimax algorithm plus pruning operation.

        Based on the minimax algorithm, 
        some branches that do not affect the result are cut out.
        """
        deepth = self.deepth
        if chessboard.color == Color.WHITE:
            index = self.max_value(chessboard, deepth, -float("inf"), float("inf"))[1]
        else:
            index = self.min_value(chessboard, deepth, -float("inf"), float("inf"))[1]

        actions = chessboard.actions()
        chessboard.move_piece(*actions[index])
        return chessboard.record

    def max_value(
        self, chessboard: ChessBoard, deepth: int, alpha: float, beta: float
    ) -> Tuple[float, int, float, float]:
        """
        Calculate the maximum value on this branch.

        Parameters
        ----------
        chessboard : ChessBoard
            Current chessboard (a copy of the original chessboard).
        deepth : int
            Remaining maximum depth (for recursive calls).
        alpha : float
            Current maximum.
        beta : float
            Current minimum.

        Returns
        -------
        val : float
            Value of this branch.
        index : int
            Index of the optimal action.
        alpha : float
            Current maximum.
        beta : float
            Current minimum.

        """
        if deepth == 0:
            return chessboard.evaluate(self.evaluate), 0, alpha, beta

        val = -float("inf")
        index = 0
        for i, s in enumerate(chessboard.actions()):
            new_chessboard = chessboard.copy().move_piece(*s)
            val = max(
                val,
                self.min_value(new_chessboard, deepth - 1, alpha, beta)[0],
            )
            if val >= beta:
                break
            if val > alpha:
                alpha = val
                index = i
        return val, index, alpha, beta

    def min_value(
        self, chessboard: ChessBoard, deepth: int, alpha: float, beta: float
    ) -> Tuple[float, int, float, float]:
        """
        Calculate the minimum value on this branch.

        Parameters
        ----------
        chessboard : ChessBoard
            Current chessboard (a copy of the original chessboard).
        deepth : int
            Remaining maximum depth (for recursive calls).
        alpha : float
            Current maximum.
        beta : float
            Current minimum.

        Returns
        -------
        val : float
            Value of this branch.
        index : int
            Index of the optimal action.
        alpha : float
            Current maximum.
        beta : float
            Current minimum.

        """
        if deepth == 0:
            return chessboard.evaluate(self.evaluate), 0, alpha, beta

        val = float("inf")
        index = 0
        for i, s in enumerate(chessboard.actions()):
            new_chessboard = chessboard.copy().move_piece(*s)
            val = min(
                val,
                self.max_value(new_chessboard, deepth - 1, alpha, beta)[0],
            )
            if val <= alpha:
                break
            if val < beta:
                beta = val
                index = i
        return val, index, alpha, beta


class BeamSearchAgent(Agent):
    """
    Agent with beam search algorithm.

    Parameters
    ----------
    evaluate : str, optional
        Value evaluation function.
    deepth : int, optional
        The maximum depth, beyond which the action sequence will be truncated.
    size : int, optional
        Maximum size per search.

    """
    def __init__(
        self,
        evaluate: Optional[str] = None,
        deepth: Optional[int] = None,
        size: Optional[int] = None,
    ) -> None:
        super().__init__()
        self.evaluate = eval(evaluate or setting.beamsearch["evaluate"])
        self.deepth = deepth or setting.beamsearch["deepth"]
        self.size = size or setting.beamsearch["size"]

    def config(self) -> dict:
        data = setting.beamsearch
        data["evaluate"] = self.evaluate.__name__
        data["deepth"] = self.deepth
        data["size"] = self.size
        return data

    def run(self, chessboard: ChessBoard) -> str:
        """
        Beam search algorithm is essentially incomplete minimax algorithm.
        
        Only some optimal actions are retained at a time, 
        rather than all of the minimax algorithm.
        """
        size = self.size
        action_sequence = []

        # Get all the action and its value
        for action in chessboard.actions():
            new_chessboard = chessboard.copy().move_piece(*action)
            val = new_chessboard.evaluate(self.evaluate)
            action_sequence.append([action, val, new_chessboard])

        # Keep only some of the best actions
        action_sequence.sort(key=lambda x: x[-2])
        if chessboard.color == Color.WHITE:
            action_sequence = action_sequence[-size:]
        else:
            action_sequence = action_sequence[:size]

        # Adopt ideas similar to minimax algorithm:
        # The white side retains the actions with the highest score, 
        # and the black side retains the X with the lowest score
        color = chessboard.color
        for _ in range(self.deepth - 1):
            color = Color.BLACK if color == Color.WHITE else Color.WHITE
            length = len(action_sequence)
            for _ in range(length):
                item = action_sequence.pop(0)
                new_action_sequence = []
                # Record the action sequence and its corresponding value 
                # in the form of tuple list
                for action in item[-1].actions():
                    new_chessboard = item[-1].copy().move_piece(*action)
                    val = new_chessboard.evaluate(self.evaluate)
                    # Expand new branch
                    new_action_sequence.append(
                        [
                            *item[:-2],
                            action,
                            val,
                            new_chessboard,
                        ]
                    )

                # Keep only some of the best actions
                new_action_sequence.sort(key=lambda x: x[-2])
                if color == Color.WHITE:
                    new_action_sequence = new_action_sequence[-size:]
                else:
                    new_action_sequence = new_action_sequence[:size]

                action_sequence.extend(new_action_sequence)

        for item in action_sequence:
            item.pop()

        # Call minimax algorithm for dict
        values = self.minimax(
            Color.BLACK if chessboard.color == Color.WHITE else Color.WHITE,
            self.todict(action_sequence),
        )
        if chessboard.color == Color.WHITE:
            extremum = max(values)
        else:
            extremum = min(values)

        # Get the index corresponding to the optimal action
        actions_dict = OrderedDict()
        for item in action_sequence:
            actions_dict[item[0]] = 1
        actions_list = list(actions_dict.keys())

        chessboard.move_piece(*actions_list[values.index(extremum)])
        return chessboard.record

    def todict(self, data: list) -> OrderedDict:
        """
        Convert tuple list to dictionary.

        Parameters
        ----------
        data : list
            Action sequence and its value.

        Returns
        -------
        tree : OrderedDict
            Dictionary form.

        Examples
        --------
        >>> agent = BeamSearchAgent()
        >>> action_sequence = [
        ...     [(((2, 8),), ((3, 6),)), (((8, 3),), ((6, 4),)), 1.8125],
        ...     [(((2, 8),), ((3, 6),)), (((2, 1),), ((3, 3),)), 4.45],
        ...     [(((2, 1),), ((3, 3),)), (((7, 1),), ((6, 3),)), 5.0],
        ...     [(((2, 1),), ((3, 3),)), (((7, 8),), ((6, 6),)), 5.0],
        ... ]
        >>> agent.todict(action_sequence)
        OrderedDict([((((2, 8),), ((3, 6),)), OrderedDict([((((8, 3),), ((6, 4),)), 1.8125), ((((2, 1),), ((3, 3),)), 4.45)])), ((((2, 1),), ((3, 3),)), OrderedDict([((((7, 1),), ((6, 3),)), 5.0), ((((7, 8),), ((6, 6),)), 5.0)]))])

        """
        tree = OrderedDict()
        for d in data:
            # If the first action is the same, it belongs to the same branch.
            if d[0] not in tree:
                tree[d[0]] = []
            if len(d) > 2:
                tree[d[0]].append(d[1:])
            # If only the last value is left, the recursion ends.
            else:
                tree[d[0]] = d[1]

        # Reduce list to subtree
        for k, v in tree.items():
            if isinstance(v, (list, tuple)):
                tree[k] = self.todict(v)

        return tree

    def minimax(self, color: Color, data: OrderedDict):
        """Minimax algorithm for dict type data implementation."""
        if isinstance(data, OrderedDict):
            values = []
            for v in data.values():
                if color == Color.WHITE:
                    value = max(self.minimax(Color.BLACK, v))
                else:
                    value = min(self.minimax(Color.WHITE, v))
                values.append(value)
            return values
        else:
            return [data]


class HumanAgent(Agent):
    """Agent operated by human."""
    def __init__(self) -> None:
        super().__init__()

    def config(self) -> dict:
        return {}

    def run(
        self, chessboard: ChessBoard, action: Union[Callable, str, List, Tuple]
    ) -> str:
        """
        Pass in a function, such as `input`, and get action by calling function;
        or pass in a string that will be parsed into actions;
        or pass an action directly.
        """
        if callable(action):
            action = action()
        if isinstance(action, str):
            action = eval(action)

        chessboard.move_piece(
            [tuple(s) for s in action[0]], [tuple(t) for t in action[1]]
        )
        return chessboard.record
