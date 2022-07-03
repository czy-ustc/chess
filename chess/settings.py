# Author       : czy
# Description  : Global settings.
#
# Copyright 2022 Zhiyuan Chen <chenzhiyuan@mail.ustc.edu.cn>

import json
from collections import UserDict
from pathlib import Path
from typing import Any

# Global default configuration.
default_setting = {
    # Names of various pieces.
    "name_list": {
        "english_name": ["King", "Queen", "Rook", "Bishop", "Knight", "Pawn"],
        "chinese_name": ["王", "后", "车", "象", "马", "兵"],
        "abbreviation": ["K", "Q", "R", "B", "N", "P"],
        "meaning": ["国王", "皇后", "战车", "主教", "骑士", "兵卒"],
    },
    # Default name.
    "display_name": "english_name",
    # The name of the piece displayed when printing the chessboard.
    "print_name": "abbreviation",
    # The action rules corresponding to various pieces.
    "rules": [
        "KingMoveRule",
        "QueenMoveRule",
        "RookMoveRule",
        "BishopMoveRule",
        "KnightMoveRule",
        "PawnMoveRule",
    ],
    # The default evaluation class.
    "evaluation_class": "QuantumValueTable",
    # Default configuration of GreedyAgent.
    "greedy": {
        "evaluate": "QuantumValueTable",
        "evaluate.optional": ["QuantumValueTable", "ValueTable", "RelativeStrength"],
    },
    # Default configuration of MinimaxAgent.
    "minimax": {
        "evaluate": "QuantumValueTable",
        "deepth": 1,
        "evaluate.optional": ["QuantumValueTable", "ValueTable", "RelativeStrength"],
        "deepth.range": [1, 3],
    },
    # Default configuration of AlphaBetaAgent.
    "alphabeta": {
        "evaluate": "QuantumValueTable",
        "deepth": 2,
        "evaluate.optional": ["QuantumValueTable", "ValueTable", "RelativeStrength"],
        "deepth.range": [2, 6],
    },
    # Default configuration of BeamSearchAgent.
    "beamsearch": {
        "evaluate": "QuantumValueTable",
        "deepth": 4,
        "size": 3,
        "evaluate.optional": ["QuantumValueTable", "ValueTable", "RelativeStrength"],
        "deepth.range": [2, 6],
        "size.range": [2, 10],
    },
    # Database file name.
    "database": "sqlite.db",
}


class Setting(UserDict):
    """Global settings."""

    def __init__(self, setting: dict = default_setting):
        super().__init__(setting)

        # Modify the configuration through JSON file to enhance scalability.
        self._path = Path(__file__).with_name("settings.json")
        if not self._path.exists():
            data = json.dumps(setting, ensure_ascii=False, indent=4)
            self._path.write_text(data, encoding="utf-8")
        else:
            conf = json.loads(self._path.read_text(encoding="utf-8"))
            self.update(conf)

    def __getattr__(self, attr: str) -> Any:
        """Get configuration item."""
        return self.get(attr, None)

    def __missing__(self, key: str) -> Any:
        """Handle missing key."""
        if isinstance(key, str):
            return None
        else:
            return self[str(key)]


# Globally unique configuration.
setting = Setting()
