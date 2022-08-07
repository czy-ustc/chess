from datetime import date, time
from functools import partial
from typing import Any, Tuple

import MySQLdb

from .constant import DataType
from .engine import Engine
from .field import Field, StorageClass


def describe(datatype: str, field: Field) -> str:
    dsc = f"{field.name} {datatype}"
    if field.unique:
        dsc += " UNIQUE"
    if not field.null:
        dsc += " NOT NULL"
    if field.autoincrement:
        dsc += " AUTO_INCREMENT"
    if datatype == "VARCHAR(%d)":
        dsc %= field.max_length or 256
    return dsc


class MysqlEngine(Engine):
    mapping = {
        DataType.String: StorageClass(
            partial(describe, "VARCHAR(%d)"),
        ),
        DataType.Integer: StorageClass(
            partial(describe, "SMALLINT"),
        ),
        DataType.Float: StorageClass(
            partial(describe, "FLOAT"),
        ),
        DataType.Boolean: StorageClass(
            partial(describe, "TINYINT"),
            decoder=bool,
            encoder=int,
        ),
        DataType.Date: StorageClass(
            partial(describe, "DATE"),
            decoder=lambda x: x if type(x) == date else x.date(),
            encoder=lambda x: x.strftime("%Y-%m-%d %H:%M:%S"),
        ),
        DataType.Time: StorageClass(
            partial(describe, "TIME"),
            decoder=lambda x: x if type(x) == time else x.time(),
            encoder=lambda x: x.strftime("%Y-%m-%d %H:%M:%S"),
        ),
        DataType.DateTime: StorageClass(
            partial(describe, "DATETIME"),
            encoder=lambda x: x.strftime("%Y-%m-%d %H:%M:%S"),
        ),
    }

    @staticmethod
    def connect(db: str, *args: Any, **kwargs: Any) -> Tuple:
        conn = MySQLdb.connect(*args, **kwargs)
        cur = conn.cursor()
        cur.execute(f"DROP DATABASE IF EXISTS {db};")
        cur.execute(f"CREATE DATABASE {db};")
        cur.execute(f"USE {db};")
        return (conn, cur)
