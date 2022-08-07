import json
import re
from typing import Any, Dict, List, Tuple

from .constant import ON_DELETE, DataType, TaskType
from .field import Field, ForeignKey, IntegerField, StorageClass
from .func import F
from .pool import Pool
from .task import Task


class Engine:
    mapping: Dict[DataType, StorageClass]
    on_delete: Dict[ON_DELETE, str] = {
        ON_DELETE.CASCADE: "CASCADE",
        ON_DELETE.PROTECT: "RESTRICT",
        ON_DELETE.SET_NULL: "SET NULL",
    }

    @staticmethod
    def connect(db: str, *args: Any, **kwargs: Any) -> Tuple:
        return NotImplemented

    def __new__(cls, *args: Any, **kwargs: Any):
        if not hasattr(cls, "_instance"):
            Engine._instance = object.__new__(cls)
        return Engine._instance

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if not hasattr(self, "conn"):
            self.conn, self.cur = self.connect(*args, **kwargs)
            Pool.processor = self
        self.cache = []

    def __call__(self, task: Task) -> None:
        return NotImplemented

    def create_table(self, model: Tuple[str, List[Field], type]) -> None:
        name, fields, meta = model

        primary_keys = []
        foreign_keys = []
        describes = []
        for field in fields:
            if field.primary_key:
                primary_keys.append(f"{field.name}")
            if isinstance(field, ForeignKey):
                foreign_keys.append(field)
                field.convert(getattr(field.to, field.to_field))

            storage = self.mapping[field.datatype]
            describes.append(storage.describe(field))

        describes.extend(f"UNIQUE({','.join(pairs)})" for pairs in meta.unique_together)

        describes.extend(
            [
                f"FOREIGN KEY({key.name}) REFERENCES {key.to._table}({key.to_field})"
                + (
                    f" ON DELETE {self.on_delete[key.on_delete]}"
                    if key.on_delete != ON_DELETE.SET
                    else ""
                )
                + " ON UPDATE CASCADE"
                for key in foreign_keys
            ]
        )
        describes.append(f"PRIMARY KEY({','.join(primary_keys)})")

        ddl = f"CREATE TABLE IF NOT EXISTS {name}({', '.join(describes)});"
        self.cur.execute(ddl)

    def insert(self, value: Tuple[type, Dict[Field, Any]]) -> dict:
        def get_pk(
            model: type,
            sql: str,
            data: List[Any],
        ) -> Tuple[Any, Tuple[Any]]:
            self.cur.execute(sql)
            self.conn.commit()
            pk = model._pk
            id = values[pk]
            if id is None and isinstance(pk, IntegerField):
                id = self.cur.lastrowid
            id = self.mapping[pk.datatype].encode(id, pk)
            sql = f"SELECT * FROM {table} WHERE {pk.name}={id} LIMIT 1;"
            self.cur.execute(sql)
            data = [*data, *self.cur.fetchone()[1:]]
            return id, data

        model, values = value
        table = model._table
        encoded_values = [
            self.mapping[k.datatype].encode(v, k) for k, v in values.items()
        ]
        data = []
        for ancestor in [*model._ancestors, model]:
            table = ancestor._table
            insert_values = encoded_values[: len(ancestor._fields)]
            sql = f"INSERT INTO {table} VALUES({','.join(insert_values)})"
            id, data = get_pk(ancestor, sql, data)
            encoded_values = [id, *encoded_values[len(ancestor._fields) :]]

        data.insert(0, json.loads(id))
        model_data = {
            k.name: self.mapping[k.datatype].decode(v, k)
            for k, v in zip(values.keys(), data)
        }
        return model_data

    @classmethod
    def to_sql(cls, model: type, value: dict) -> str:
        def get_table_name(model: type) -> str:
            if not model._ancestors:
                return model._table
            table_name = model._table
            for ancestor in model._ancestors:
                table_name = f"(SELECT * FROM {table_name} NATURAL JOIN {ancestor._table}) {model._table}"
            return table_name

        if value["from"]:
            from_clause = (
                f"({cls.to_sql(model, value['from']).rstrip(';')}) {model._table}"
            )
        else:
            for idx, (k, (q, v)) in enumerate(value["join"].items()):
                name = (
                    get_table_name(k)
                    if not q
                    else f"({cls.to_sql(k, q).rstrip(';')}) {k._table}"
                )
                if idx == 0:
                    from_clause = name
                    continue
                expr = ",".join(f"{t1}.{f1}={t2}.{f2}" for (t1, f1), (t2, f2) in v)
                if expr:
                    from_clause = f"({from_clause} INNER JOIN {name} ON {expr})"
                else:
                    from_clause = f"(SELECT * FROM {from_clause} NATURAL JOIN {name}) {model._table}"

        select_clause = ",".join(f"{v} '{k}'" for k, v in value["select"].items())
        distinct_clause = "DISTINCT" if value["distinct"] else ""
        where_clause = value["where"] and f"WHERE {value['where']}"
        group_by_clause = (
            value["group_by"] and f"GROUP BY {','.join(value['group_by'])}"
        )
        order_by_clause = (
            (value["order_by"] or "")
            and f"ORDER BY {','.join(f'{x[1:]} DESC' if x.startswith('-') else f'{x} ASC' for x in value['order_by'])}"
        )

        limit_clause = value["limit"] and "LIMIT {} OFFSET {}".format(*value["limit"])
        sql = f"SELECT {distinct_clause} {select_clause} FROM {from_clause} {where_clause} {group_by_clause} {order_by_clause} {limit_clause};"

        def repl(matched: re.Match):
            _model = model
            *fks, field = matched.group(1).split("__")
            for fk in fks:
                _model = getattr(_model, fk).to
            return f"{_model._table}.{field}"

        sql = re.sub("`(\\w+__\\w+)`", repl, sql)
        sql = re.sub("`(\\w+)`", f"{model._table}.\\1", sql)
        return sql

    def query(self, value: Tuple[type, dict]) -> List[Dict[str, Any]]:
        model, values = value
        sql = self.to_sql(model, values)
        self.cur.execute(sql)
        rows = self.cur.fetchall()
        description = tuple(values["select"].keys())
        datatype = tuple(v.gettype(model._fields) for v in values["select"].values())

        datas = [
            {
                k: self.mapping[t].decode(v, getattr(model, k, None))
                if t in self.mapping
                else v
                for k, t, v in zip(description, datatype, d)
            }
            for d in rows
        ]
        return datas

    def update(self, value: Tuple[type, dict, Dict[str, Any]]) -> int:
        model, query, new_value = value
        pk = model._pk.name

        new_value = {
            k.name: self.mapping[k.datatype].encode(v, k)
            if not isinstance(v, F)
            else str(v)
            for k, v in new_value.items()
        }
        new_pk = new_value.pop(pk, None) if model._ancestors else None

        query["select"] = {pk: pk}
        nested_clause = f"WHERE {pk} IN (SELECT {pk} FROM ({self.to_sql(model, query).rstrip(';')}) TEMP)"
        table = model._table
        rowcount = 0
        fields = set()
        for ancestor in [*model._ancestors, model]:
            table = ancestor._table
            fields = {f.name for f in ancestor._fields} - fields
            update_clause = ",".join(
                f"{F(k)}={v}" for k, v in new_value.items() if k in fields
            )
            if update_clause:
                sql = f"UPDATE {table} SET {update_clause} {nested_clause};"
                try:
                    self.cur.execute(sql)
                except Exception as e:
                    print(sql, "\n", e)
                    raise ValueError
                self.conn.commit()
                rowcount = max(rowcount, self.cur.rowcount)

        if new_pk is not None:
            table = model._ancestors[0]._table
            sql = f"UPDATE {table} SET {F(pk)}={new_pk} {nested_clause};"
            self.cur.execute(sql)
            self.conn.commit()
            rowcount = max(rowcount, self.cur.rowcount)

        return rowcount

    def delete(self, value: Tuple[type, dict]) -> int:
        model, values = value
        pk = model._pk.name
        values["select"] = {pk: pk}
        nested_clause = (
            f"(SELECT {pk} FROM ({self.to_sql(model, values).rstrip(';')}) TEMP)"
        )

        for obj, fk in model._refs:
            if fk.on_delete_set is not None:
                value = fk.on_delete_set
                if callable(value):
                    value = value()
                sql = f"UPDATE {obj._table} SET {F(fk.name) == value} WHERE {fk.name} IN {nested_clause};"
                self.cur.execute(sql)
                self.conn.commit()

        table = model._table
        if model._ancestors:
            table = model._ancestors[0]._table
        sql = f"DELETE FROM {table} WHERE {pk} IN {nested_clause};"
        self.cur.execute(sql)
        self.conn.commit()
        return self.cur.rowcount

    def __call__(self, task: Task) -> None:
        if task.tasktype == TaskType.CREATE_TABLE:
            return self.create_table(task.value)
        elif task.tasktype == TaskType.INSERT:
            return self.insert(task.value)
        elif task.tasktype == TaskType.QUERY:
            return self.query(task.value)
        elif task.tasktype == TaskType.UPDATE:
            return self.update(task.value)
        elif task.tasktype == TaskType.DELETE:
            return self.delete(task.value)
