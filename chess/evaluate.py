# Author       : czy
# Description  : Chessboard value evaluation classes.
#
# Copyright 2022 Zhiyuan Chen <chenzhiyuan@mail.ustc.edu.cn>

import abc

from chess.constant import Color


class Evaluate(metaclass=abc.ABCMeta):
    """The base class of all evaluation classes."""

    @abc.abstractmethod
    def evaluate(data: dict) -> float:
        """
        Input chessboard data and output the assessed value.
        
        Notes
        -----
        If the white player is dominant, the value is greater than 0, 
        otherwise the value is less than 0.

        """
        pass


class RelativeStrength(Evaluate):
    """
    Evaluate the situation according to 
    the relative strength value of the chess pieces.

    Notes
    -----
    This relative strength value refers to 
    the relative strength of standard chess pieces from Wikipedia.
    (This means that no quantum effects are considered.)

    """
    pawn_white_value = 10
    pawn_black_value = -pawn_white_value
    knight_white_value = 30
    knight_black_value = -knight_white_value
    bishop_white_value = 30
    bishop_black_value = -bishop_white_value
    rook_white_value = 50
    rook_black_value = -rook_white_value
    queen_white_value = 90
    queen_black_value = -queen_white_value
    king_white_value = 900
    king_black_value = -king_white_value

    @staticmethod
    def evaluate(data: dict) -> float:
        """Calculate the total value of the currently surviving pieces."""
        total_value = 0
        for _, v in data.items():
            color, name, probability = v
            value = eval(
                f"RelativeStrength.{name.name.lower()}_{color.name.lower()}_value"
            )
            total_value += value * probability
        return total_value


class ValueTable(Evaluate):
    """
    Evaluate the situation according to 
    the relative strength value 
    and place on the chessboard of the chess pieces.

    Notes
    -----
    It also refers to Wikipedia without any quantum correction.

    """
    pawn_white_value_correct = [
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0],
        [1.0, 1.0, 2.0, 3.0, 3.0, 2.0, 1.0, 1.0],
        [0.5, 0.5, 1.0, 2.5, 2.5, 1.0, 0.5, 0.5],
        [0.0, 0.0, 0.0, 2.0, 2.0, 0.0, 0.0, 0.0],
        [0.5, -0.5, -1.0, 0.0, 0.0, -1.0, -0.5, 0.5],
        [0.5, 1.0, 1.0, -2.0, -2.0, 1.0, 1.0, 0.5],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    ]

    pawn_black_value_correct = pawn_white_value_correct[::-1]

    knight_white_value_correct = knight_black_value_correct = [
        [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0],
        [-4.0, -2.0, 0.0, 0.0, 0.0, 0.0, -2.0, -4.0],
        [-3.0, 0.0, 1.0, 1.5, 1.5, 1.0, 0.0, -3.0],
        [-3.0, 0.5, 1.5, 2.0, 2.0, 1.5, 0.5, -3.0],
        [-3.0, 0.0, 1.5, 2.0, 2.0, 1.5, 0.0, -3.0],
        [-3.0, 0.5, 1.0, 1.5, 1.5, 1.0, 0.5, -3.0],
        [-4.0, -2.0, 0.0, 0.5, 0.5, 0.0, -2.0, -4.0],
        [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0],
    ]

    bishop_white_value_correct = [
        [-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0],
        [-1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0],
        [-1.0, 0.0, 0.5, 1.0, 1.0, 0.5, 0.0, -1.0],
        [-1.0, 0.5, 0.5, 1.0, 1.0, 0.5, 0.5, -1.0],
        [-1.0, 0.0, 1.0, 1.0, 1.0, 1.0, 0.0, -1.0],
        [-1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0],
        [-1.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.5, -1.0],
        [-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0],
    ]

    bishop_black_value_correct = bishop_white_value_correct[::-1]

    rook_white_value_correct = [
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.5],
        [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
        [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
        [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
        [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
        [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
        [0.0, 0.0, 0.0, 0.5, 0.5, 0.0, 0.0, 0.0],
    ]

    rook_black_value_correct = rook_white_value_correct[::-1]

    queen_white_value_correct = queen_black_value_correct = [
        [-2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0],
        [-1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0],
        [-1.0, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -1.0],
        [-0.5, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -0.5],
        [0.0, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -0.5],
        [-1.0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.0, -1.0],
        [-1.0, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0, -1.0],
        [-2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0],
    ]

    king_white_value_correct = [
        [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
        [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
        [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
        [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
        [-2.0, -3.0, -3.0, -4.0, -4.0, -3.0, -3.0, -2.0],
        [-1.0, -2.0, -2.0, -2.0, -2.0, -2.0, -2.0, -1.0],
        [2.0, 2.0, 0.0, 0.0, 0.0, 0.0, 2.0, 2.0],
        [2.0, 3.0, 1.0, 0.0, 0.0, 1.0, 3.0, 2.0],
    ]

    king_black_value_correct = king_white_value_correct[::-1]

    @staticmethod
    def evaluate(data: dict) -> float:
        """Calculate the total value of the currently surviving pieces."""
        total_value = 0
        for k, v in data.items():
            col, row = k[0] - 1, k[1] - 1
            color, name, probability = v
            table = eval(
                f"ValueTable.{name.name.lower()}_{color.name.lower()}_value_correct"
            )
            value = eval(
                f"RelativeStrength.{name.name.lower()}_{color.name.lower()}_value"
            )
            if color == Color.WHITE:
                total_value += (value + table[row][col]) * probability
            else:
                total_value += (value - table[row][col]) * probability
        return total_value


class QuantumValueTable(Evaluate):
    """
    On the basis of the above evaluation class, 
    the quantum effect is considered. 
    The evaluation matrix of the place of the chess pieces is fine tuned, 
    and the consideration of separation is added.
    """

    # In order to improve the speed as much as possible, 
    # all evaluation matrices are stored in a list.
    value_table = [
        # White
        [
            # King
            [
                [197.0, 196.0, 196.0, 195.0, 195.0, 196.0, 196.0, 197.0],
                [197.0, 196.0, 196.0, 195.0, 195.0, 196.0, 196.0, 197.0],
                [197.0, 196.0, 196.0, 195.0, 195.0, 196.0, 196.0, 197.0],
                [197.0, 196.0, 196.0, 195.0, 195.0, 196.0, 196.0, 197.0],
                [198.0, 197.0, 197.0, 196.0, 196.0, 197.0, 197.0, 198.0],
                [199.0, 198.0, 198.0, 198.0, 198.0, 198.0, 198.0, 199.0],
                [202.0, 202.0, 200.0, 200.0, 200.0, 200.0, 202.0, 202.0],
                [202.0, 203.0, 201.0, 200.0, 200.0, 201.0, 203.0, 202.0],
            ],
            # Queen
            [
                [88.0, 89.0, 89.0, 89.5, 89.5, 89.0, 89.0, 88.0],
                [89.0, 90.0, 90.0, 90.0, 90.0, 90.0, 90.0, 89.0],
                [89.0, 90.0, 90.5, 90.5, 90.5, 90.5, 90.0, 89.0],
                [89.5, 90.0, 90.5, 90.5, 90.5, 90.5, 90.0, 89.5],
                [90.0, 90.0, 90.5, 90.5, 90.5, 90.5, 90.0, 89.5],
                [89.0, 90.5, 90.5, 90.5, 90.5, 90.5, 90.0, 89.0],
                [89.0, 90.0, 90.5, 90.0, 90.0, 90.0, 90.0, 89.0],
                [88.0, 89.0, 89.0, 89.5, 89.5, 89.0, 89.0, 88.0],
            ],
            # Rook
            [
                [50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0],
                [50.5, 51.0, 51.0, 51.0, 51.0, 51.0, 51.0, 50.5],
                [49.5, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 49.5],
                [49.5, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 49.5],
                [49.5, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 49.5],
                [49.5, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 49.5],
                [49.5, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 49.5],
                [50.0, 50.0, 50.0, 50.5, 50.5, 50.0, 50.0, 50.0],
            ],
            # Bishop
            [
                [28.0, 29.0, 29.0, 29.0, 29.0, 29.0, 29.0, 28.0],
                [29.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 29.0],
                [29.0, 30.0, 30.5, 31.0, 31.0, 30.5, 30.0, 29.0],
                [29.0, 30.5, 30.5, 31.0, 31.0, 30.5, 30.5, 29.0],
                [29.0, 30.0, 31.0, 31.0, 31.0, 31.0, 30.0, 29.0],
                [29.0, 31.0, 31.0, 31.0, 31.0, 31.0, 31.0, 29.0],
                [29.0, 30.5, 30.0, 30.0, 30.0, 30.0, 30.5, 29.0],
                [28.0, 29.0, 29.0, 29.0, 29.0, 29.0, 29.0, 28.0],
            ],
            # Knight
            [
                [25.0, 26.0, 27.0, 27.0, 27.0, 27.0, 26.0, 25.0],
                [26.0, 28.0, 30.0, 30.0, 30.0, 30.0, 28.0, 26.0],
                [27.0, 30.0, 31.0, 31.5, 31.5, 31.0, 30.0, 27.0],
                [27.0, 30.5, 31.5, 32.0, 32.0, 31.5, 30.5, 27.0],
                [27.0, 30.0, 31.5, 32.0, 32.0, 31.5, 30.0, 27.0],
                [27.0, 30.5, 31.0, 31.5, 31.5, 31.0, 30.5, 27.0],
                [26.0, 28.0, 30.0, 30.5, 30.5, 30.0, 28.0, 26.0],
                [25.0, 26.0, 27.0, 27.0, 27.0, 27.0, 26.0, 25.0],
            ],
            # Pawn
            [
                [10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0],
                [15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0],
                [11.0, 11.0, 12.0, 13.0, 13.0, 12.0, 11.0, 11.0],
                [15.5, 10.5, 11.0, 12.5, 12.5, 11.0, 10.5, 15.5],
                [10.0, 10.0, 10.0, 12.0, 12.0, 10.0, 10.0, 10.0],
                [10.5, 9.5, 9.0, 10.0, 10.0, 9.0, 9.5, 10.5],
                [10.5, 11.0, 11.0, 8.0, 8.0, 11.0, 11.0, 10.5],
                [80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0],
            ],
        ],
        # Black
        [
            # King
            [
                [-202.0, -203.0, -201.0, -200.0, -200.0, -201.0, -203.0, -202.0],
                [-202.0, -202.0, -200.0, -200.0, -200.0, -200.0, -202.0, -202.0],
                [-199.0, -198.0, -198.0, -198.0, -198.0, -198.0, -198.0, -199.0],
                [-198.0, -197.0, -197.0, -196.0, -196.0, -197.0, -197.0, -198.0],
                [-197.0, -196.0, -196.0, -195.0, -195.0, -196.0, -196.0, -197.0],
                [-197.0, -196.0, -196.0, -195.0, -195.0, -196.0, -196.0, -197.0],
                [-197.0, -196.0, -196.0, -195.0, -195.0, -196.0, -196.0, -197.0],
                [-197.0, -196.0, -196.0, -195.0, -195.0, -196.0, -196.0, -197.0],
            ],
            # Queen
            [
                [-88.0, -89.0, -89.0, -89.5, -89.5, -89.0, -89.0, -88.0],
                [-89.0, -90.0, -90.0, -90.0, -90.0, -90.0, -90.0, -89.0],
                [-89.0, -90.0, -90.5, -90.5, -90.5, -90.5, -90.0, -89.0],
                [-89.5, -90.0, -90.5, -90.5, -90.5, -90.5, -90.0, -89.5],
                [-90.0, -90.0, -90.5, -90.5, -90.5, -90.5, -90.0, -89.5],
                [-89.0, -90.5, -90.5, -90.5, -90.5, -90.5, -90.0, -89.0],
                [-89.0, -90.0, -90.5, -90.0, -90.0, -90.0, -90.0, -89.0],
                [-88.0, -89.0, -89.0, -89.5, -89.5, -89.0, -89.0, -88.0],
            ],
            # Rook
            [
                [-50.0, -50.0, -50.0, -50.5, -50.5, -50.0, -50.0, -50.0],
                [-49.5, -50.0, -50.0, -50.0, -50.0, -50.0, -50.0, -49.5],
                [-49.5, -50.0, -50.0, -50.0, -50.0, -50.0, -50.0, -49.5],
                [-49.5, -50.0, -50.0, -50.0, -50.0, -50.0, -50.0, -49.5],
                [-49.5, -50.0, -50.0, -50.0, -50.0, -50.0, -50.0, -49.5],
                [-49.5, -50.0, -50.0, -50.0, -50.0, -50.0, -50.0, -49.5],
                [-50.5, -51.0, -51.0, -51.0, -51.0, -51.0, -51.0, -50.5],
                [-50.0, -50.0, -50.0, -50.0, -50.0, -50.0, -50.0, -50.0],
            ],
            # Bishop
            [
                [-28.0, -29.0, -29.0, -29.0, -29.0, -29.0, -29.0, -28.0],
                [-29.0, -30.5, -30.0, -30.0, -30.0, -30.0, -30.5, -29.0],
                [-29.0, -31.0, -31.0, -31.0, -31.0, -31.0, -31.0, -29.0],
                [-29.0, -30.0, -31.0, -31.0, -31.0, -31.0, -30.0, -29.0],
                [-29.0, -30.5, -30.5, -31.0, -31.0, -30.5, -30.5, -29.0],
                [-29.0, -30.0, -30.5, -31.0, -31.0, -30.5, -30.0, -29.0],
                [-29.0, -30.0, -30.0, -30.0, -30.0, -30.0, -30.0, -29.0],
                [-28.0, -29.0, -29.0, -29.0, -29.0, -29.0, -29.0, -28.0],
            ],
            # Knight
            [
                [-25.0, -26.0, -27.0, -27.0, -27.0, -27.0, -26.0, -25.0],
                [-26.0, -28.0, -30.0, -30.0, -30.0, -30.0, -28.0, -26.0],
                [-27.0, -30.0, -31.0, -31.5, -31.5, -31.0, -30.0, -27.0],
                [-27.0, -30.5, -31.5, -32.0, -32.0, -31.5, -30.5, -27.0],
                [-27.0, -30.0, -31.5, -32.0, -32.0, -31.5, -30.0, -27.0],
                [-27.0, -30.5, -31.0, -31.5, -31.5, -31.0, -30.5, -27.0],
                [-26.0, -28.0, -30.0, -30.5, -30.5, -30.0, -28.0, -26.0],
                [-25.0, -26.0, -27.0, -27.0, -27.0, -27.0, -26.0, -25.0],
            ],
            # Pawn
            [
                [-80.0, -80.0, -80.0, -80.0, -80.0, -80.0, -80.0, -80.0],
                [-10.5, -11.0, -11.0, -8.0, -8.0, -11.0, -11.0, -10.5],
                [-10.5, -9.5, -9.0, -10.0, -10.0, -9.0, -9.5, -10.5],
                [-10.0, -10.0, -10.0, -12.0, -12.0, -10.0, -10.0, -10.0],
                [-15.5, -10.5, -11.0, -12.5, -12.5, -11.0, -10.5, -15.5],
                [-11.0, -11.0, -12.0, -13.0, -13.0, -12.0, -11.0, -11.0],
                [-15.0, -15.0, -15.0, -15.0, -15.0, -15.0, -15.0, -15.0],
                [-10.0, -10.0, -10.0, -10.0, -10.0, -10.0, -10.0, -10.0],
            ],
        ],
    ]

    # According to the rules of quantum chess, 
    # more separation will help improve the survival rate of chess pieces.
    # Therefore, consider rewarding actions that generate more separation.
    # Each item in the following list consists of two values: 
    # threshold and scale factor.
    # The threshold is set to avoid excessive splitting of chess pieces.
    # The scale factor represents the reward for separation.
    probability_table = [
        # King
        [0.1, 0.03],
        # Queen
        [0.2, 0.02],
        # Rook
        [0.3, 0.04],
        # Bishop
        [0.3, 0.03],
        # Knight
        [0.3, 0.05],
        # Pawn
        [0, 0],
    ]

    @staticmethod
    def evaluate(data: dict) -> float:
        """Calculate the total value of the currently surviving pieces."""
        total_value = 0
        value_table = QuantumValueTable.value_table
        probability_table = QuantumValueTable.probability_table
        for k, v in data.items():
            col, row = k[0] - 1, k[1] - 1
            color, name, probability = v
            # Reward actions with multiple distractions
            if probability > probability_table[name.value][0]:
                probability += (1 - probability) * probability_table[name.value][1]
            total_value += value_table[color.value][name.value][row][col] * probability
        return total_value
