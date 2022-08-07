import json
import sqlite3
from datetime import datetime, timedelta
from functools import partial
from math import ceil, floor
from typing import Any, Tuple

from .constant import DataType
from .engine import Engine
from .field import Field, StorageClass


def describe(datatype: str, field: Field) -> str:
    dsc = f"{field.name} {datatype}"
    if field.unique:
        dsc += " UNIQUE"
    if not field.null:
        dsc += " NOT NULL"
    return dsc


class SqiteEngine(Engine):
    mapping = {
        DataType.String: StorageClass(
            partial(describe, "TEXT"),
            decoder=lambda x: json.loads(f'"{x}"'),
        ),
        DataType.Integer: StorageClass(
            partial(describe, "INTEGER"),
        ),
        DataType.Float: StorageClass(
            partial(describe, "REAL"),
        ),
        DataType.Boolean: StorageClass(
            partial(describe, "INTEGER"),
            decoder=bool,
            encoder=int,
        ),
        DataType.Date: StorageClass(
            partial(describe, "TEXT"),
            decoder=lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S").date(),
            encoder=lambda x: x.strftime("%Y-%m-%d %H:%M:%S"),
        ),
        DataType.Time: StorageClass(
            partial(describe, "TEXT"),
            decoder=lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S").time(),
            encoder=lambda x: x.strftime("%Y-%m-%d %H:%M:%S"),
        ),
        DataType.DateTime: StorageClass(
            partial(describe, "TEXT"),
            decoder=lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S"),
            encoder=lambda x: x.strftime("%Y-%m-%d %H:%M:%S"),
        ),
    }

    @staticmethod
    def connect(db: str, *args: Any, **kwargs: Any) -> Tuple:
        conn = sqlite3.connect(db, *args, **kwargs)
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys=ON;")
        conn.create_function("CONCAT", -1, lambda *args: "".join(args))
        conn.create_function("FLOOR", 1, lambda x: floor(x))
        conn.create_function("CEIL", 1, lambda x: ceil(x))
        conn.create_function("ROUND", 2, lambda x, n=0: round(x, n))
        conn.create_function(
            "DATE_FORMAT",
            2,
            lambda x, y: datetime.strptime(x, "%Y-%m-%d %H:%M:%S").strftime(y),
        )
        conn.create_function(
            "DATEDIFF",
            2,
            lambda x, y: (
                datetime.strptime(x, "%Y-%m-%d %H:%M:%S")
                - datetime.strptime(y, "%Y-%m-%d %H:%M:%S")
            ).days,
        )
        conn.create_function(
            "ADDDATE",
            2,
            lambda d, n: (
                datetime.strptime(d, "%Y-%m-%d %H:%M:%S") + timedelta(days=n)
            ).strftime("%Y-%m-%d %H:%M:%S"),
        )
        conn.create_function(
            "ADDTIME",
            2,
            lambda t, n: (
                datetime.strptime(t, "%Y-%m-%d %H:%M:%S") + timedelta(seconds=n)
            ).strftime("%Y-%m-%d %H:%M:%S"),
        )
        conn.create_function(
            "SUBDATE",
            2,
            lambda d, n: (
                datetime.strptime(d, "%Y-%m-%d %H:%M:%S") - timedelta(days=n)
            ).strftime("%Y-%m-%d %H:%M:%S"),
        )
        conn.create_function(
            "SUBTIME",
            2,
            lambda t, n: (
                datetime.strptime(t, "%Y-%m-%d %H:%M:%S") - timedelta(seconds=n)
            ).strftime("%Y-%m-%d %H:%M:%S"),
        )
        return (conn, cur)
