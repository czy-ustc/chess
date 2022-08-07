import re
from functools import reduce
from random import choice, choices
from typing import Any, Dict, Iterator, List, Optional, Union

from .constant import TaskType
from .func import Count, F
from .pool import Pool
from .task import Task


class Table:
    def __init__(self, model: type) -> None:
        self._model = model
        self._query = {
            "join": {model: ({}, ())},
            "from": {},
            "select": {},
            "distinct": False,
            "where": "",
            "group_by": "",
            "order_by": model.Meta.ordering,
            "limit": "",
        }
        self.condition = {}

    def join(self, table: "Table") -> "Table":
        model = table._model
        if not table._query["select"]:
            table.select(*[field.name for field in model._fields])
        models = [model] + list(self._query["join"].keys())
        models = sorted(set(models), key=models.index)

        self._query["join"] = {
            obj: (
                table._query if table._model == obj else None,
                tuple(
                    ((field.to._table, field.to_field), (obj._table, field.name))
                    for field in obj._fields
                    if getattr(field, "to", None) in models[:index]
                    or getattr(field, "to", None) in model._ancestors
                ),
            )
            for index, obj in enumerate(models)
        }
        return self

    def insert(self, *args: Dict[str, Any], **kwargs: Any) -> Any:
        for arg in args:
            kwargs.update(arg)
        kwargs = {**self.condition, **kwargs}
        model = self._model
        fields = model._fields
        values = {k: kwargs.get(k.name, None) for k in fields}
        model_datas = Pool.add(Task(TaskType.INSERT, (model, values)))
        model_datas.setdefault("__id", model_datas[model._pk.name])
        return self._model(model_datas)

    def select(self, *args: Union[str, F], **kwargs: Union[str, F]) -> "Table":
        if self._query["select"]:
            self._query = {
                "join": {},
                "from": self._query,
                "select": {},
                "distinct": False,
                "where": "",
                "group_by": "",
                "order_by": tuple(self._query["select"].keys()),
                "limit": "",
            }
        columns = {str(x): F(x) for x in args}
        columns.update({k: F(v) for k, v in kwargs.items()})
        self._query["select"] = columns

        model = self._model
        for matched in re.findall(
            "`(\\w+__\\w+)`", " ".join(str(v) for v in columns.values())
        ):
            while True:
                try:
                    fk, matched = matched.split("__", 1)
                except ValueError:
                    break
                model = getattr(model, fk).to
                self.join(Table(model))
        return self

    def distinct(self) -> "Table":
        self._query["distinct"] = True
        return self

    def where(self, *args: F, **kwargs: Union[Any, F]) -> "Table":
        self.condition.update(
            {
                k: v
                for k, v in kwargs.items()
                if not isinstance(v, F) and k in [f.name for f in self._model._fields]
            }
        )
        condtion = reduce(
            lambda x, y: x & y,
            [F(x) for x in args] + [F(k) == v for k, v in kwargs.items()],
        )

        if isinstance(self._query["where"], str):
            self._query["where"] = condtion
        else:
            self._query["where"] &= condtion

        model = self._model
        for matched in re.findall("`(\\w+__\\w+)`", str(condtion)):
            while True:
                try:
                    fk, matched = matched.split("__", 1)
                except ValueError:
                    break
                model = getattr(model, fk).to
                self.join(Table(model))

        return self

    def limit(self, count: int, offset: int = 0) -> "Table":
        self._query["limit"] = (count, offset)
        return self

    def order_by(self, *args: str) -> "Table":
        if len(args) == 0:
            return self
        self._query["order_by"] = args
        return self

    def group_by(self, *args: str) -> "Table":
        self._query["group_by"] = list(args) or ""
        return self

    @property
    def data(self) -> List[Any]:
        pk = self._model._pk.name
        selected = True
        if not self._query["select"]:
            selected = False
            self.select(*[field.name for field in self._model._fields])
        raw_datas = Pool.add(Task(TaskType.QUERY, (self._model, self._query)))
        if not selected and not self._query["from"]:
            return [self._model({"__id": d[pk], **d}) for d in raw_datas]
        return [self._model.transform(d) for d in raw_datas]

    def __str__(self) -> str:
        return f"Query<{self.data}>"

    def __getitem__(self, index: Union[int, slice]) -> Union[Any, List[Any]]:
        return self.data[index]

    def __iter__(self) -> Iterator[Any]:
        return self.data.__iter__()

    def reverse(self) -> "Table":
        self._query["order_by"] = tuple(
            x[1:] if x.startswith("-") else "-" + x for x in self._query["order_by"]
        )
        return self

    def get(self, pk: Any) -> Any:
        return self.where(**{self._model._pk.name: pk}).limit(1).data[0]

    def first(self) -> Any:
        query = self.limit(1)
        return query.data[0]

    def last(self) -> Any:
        return self.reverse().first()

    def rand(self, n: Optional[int] = None) -> Union[Any, List[Any]]:
        if n is None:
            return choice(self.data)
        else:
            return choices(self.data, k=n)

    def count(self) -> int:
        return self.select(count=Count("*")).limit(1)[0]["count"]

    def exists(self) -> bool:
        try:
            self.limit(1)[0]
            return True
        except IndexError:
            return False

    def update(self, *args: Dict[str, Any], **kwargs: Any) -> int:
        for arg in args:
            kwargs.update(arg)
        if len(kwargs) == 0:
            return 0

        kwargs = {k: kwargs[k.name] for k in self._model._fields if k.name in kwargs}
        return Pool.add(Task(TaskType.UPDATE, (self._model, self._query, kwargs)))

    def delete(self) -> int:
        return Pool.add(Task(TaskType.DELETE, (self._model, self._query)))


class MultTable(Table):
    def __init__(self, model: type) -> None:
        super().__init__(model)
        self._related_tables = []

    def join(self, table: "Table") -> "Table":
        self._related_tables.append(table)
        return super().join(table)

    def insert(self, *args: Dict[str, Any], **kwargs: Any) -> Any:
        obj = super().insert(*args, **kwargs)
        for table in self._related_tables:
            table.insert(*args, **kwargs)
        return obj

    def add(
        self,
        obj: Any,
        *args: Dict[str, Any],
        **kwargs: Any,
    ) -> "MultTable":
        kwargs[self._model._pk.name] = obj
        for table in self._related_tables:
            table.insert(*args, **kwargs)
        return self

    def remove(self, obj: Any) -> "MultTable":
        condition = {self._model._pk.name: obj}
        for table in self._related_tables:
            table.where(**condition).delete()
        return self

    def clear(self) -> "MultTable":
        for table in self._related_tables:
            table.delete()
        return self
