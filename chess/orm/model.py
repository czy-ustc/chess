from typing import Any, Dict, Optional, Tuple

from .constant import ON_DELETE, Event, TaskType, When
from .field import Field, ForeignKey, IntegerField, ManyToManyField
from .pool import Pool
from .signal import Signal
from .table import MultTable, Table
from .task import Task


class ModelBase(type):
    def __new__(cls, name: str, bases: tuple, attrs: dict) -> type:
        many_to_many = []
        for key, value in attrs.items():
            if isinstance(value, ManyToManyField):
                many_to_many.append((key, value))
        for key, _ in many_to_many:
            attrs.pop(key)

        new_class = super().__new__(cls, name, bases, attrs)
        if name == "Model":
            return new_class

        base = bases[0]
        ancestors = []
        while base.__name__ != "Model":
            ancestors.append(base)
            base = base.__bases__[0]
        ancestors.reverse()

        pk = None
        fks = []
        fields = []
        for key, value in attrs.items():
            if isinstance(value, Field):
                value.name = key
                fields.append(value)
                if value.primary_key:
                    assert pk is None
                    pk = value
                if isinstance(value, ForeignKey):
                    fks.append(value)

        if ancestors:
            pk = ancestors[0]._pk
            fk = ForeignKey(
                to=ancestors[0],
                to_field=pk.name,
                on_delete=ON_DELETE.CASCADE,
                primary_key=True,
            )
            fk.convert(pk)
            fk.name = pk.name
            fields.insert(0, fk)

        if pk is None:
            _id = IntegerField(
                primary_key=True,
                autoincrement=True,
            )
            _id.name = "_id"
            new_class._id = _id
            fields.insert(0, _id)
            pk = _id

        new_class.Meta = type("Meta", (new_class.Meta,), {})
        if not hasattr(new_class.Meta, "ordering") or new_class.Meta.ordering is None:
            new_class.Meta.ordering = (pk.name,)

        if (
            not hasattr(new_class.Meta, "unique_together")
            or new_class.Meta.unique_together is None
        ):
            new_class.Meta.unique_together = ()

        Pool.add(Task(TaskType.CREATE_TABLE, (name, fields, new_class.Meta)))

        new_class._table = name
        new_class._pk = pk
        new_class._ancestors = tuple(ancestors)
        new_class._refs = ()
        if ancestors:
            new_class._fields = tuple([*ancestors[-1]._fields, *fields[1:]])
            new_class._fks = tuple([*ancestors[-1]._fks, *fks])
        else:
            new_class._fields = tuple(fields)
            new_class._fks = tuple(fks)

        def set_fk(fk: ForeignKey) -> None:
            setattr(
                fk.to,
                fk.related_name or f"{name.lower()}_set",
                property(
                    lambda x: Table(new_class).where(
                        **{fk.name: getattr(x, x._pk.name)}
                    )
                ),
            )

        for fk in new_class._fks:
            fk.to._refs = (*fk.to._refs, (new_class, fk))
            set_fk(fk)

        for key, value in many_to_many:
            related_name = value.related_name or f"{name.lower()}_set"
            _from = ForeignKey(new_class, related_name=key, on_delete=ON_DELETE.CASCADE)
            _to = ForeignKey(
                value.to,
                related_name=related_name,
                on_delete=ON_DELETE.CASCADE,
            )
            from_name = _from.to_field
            to_name = _to.to_field
            if from_name == to_name:
                from_name = f"{name.lower()}_{from_name}"
                to_name = f"{value.to._table.lower()}_{to_name}"
            relationship = type(
                f"{name}_{value.to._table}",
                (Model,),
                {
                    from_name: _from,
                    to_name: _to,
                    "Meta": type(
                        "Meta", (), {"unique_together": ((from_name, to_name),)}
                    ),
                    **value.extras,
                },
            )
            setattr(
                _from.to,
                _from.related_name,
                property(
                    lambda x: MultTable(_to.to).join(
                        Table(relationship).where(**{from_name: getattr(x, x._pk.name)})
                    )
                ),
            )
            setattr(
                _to.to,
                _to.related_name,
                property(
                    lambda x: MultTable(_from.to).join(
                        Table(relationship).where(**{to_name: getattr(x, x._pk.name)})
                    )
                ),
            )
        return new_class


class Model(metaclass=ModelBase):
    _table: str
    _fields: Tuple[Field]
    _pk: Field
    _fks: Tuple[Field]
    _refs: Tuple[Tuple["Model", Field]]
    _ancestors: Tuple["Model"]

    @classmethod
    def transform(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        for k, v in values.items():
            field = getattr(cls, k, None)
            if v is not None and isinstance(field, ForeignKey):
                values[k] = Table(field.to).where(**{field.to_field: v}).first()
        return values

    def __init__(self, *args: Dict[str, Any], **kwargs: Any) -> None:
        for arg in args:
            kwargs.update(arg)
        self.__id = kwargs.pop("__id", None)
        for field, value in self.transform(kwargs).items():
            setattr(self, field, value)

    def __str__(self) -> str:
        data = {
            field.name: getattr(self, field.name)
            if not isinstance(getattr(self, field.name), Field)
            else None
            for field in self._fields
        }
        return f"{self._table}<[{data}]>"

    def __repr__(self) -> str:
        return f"{self._table} object ({repr(getattr(self, self._pk.name))})"

    def __eq__(self, obj: object) -> bool:
        if type(self) != type(obj):
            return False
        return self.pk == obj.pk

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    @property
    def pk(self) -> Any:
        return self.__id

    def flush(self) -> "Model":
        obj = Table(self.__class__).get(getattr(self, self._pk.name))
        for field in self._fields:
            setattr(self, field.name, getattr(obj, field.name))
        return self

    def save(self) -> "Model":
        def get_values() -> dict:
            values = {}
            for field in self.__class__._fields:
                if not isinstance(getattr(self, field.name), Field):
                    values[field.name] = getattr(self, field.name)
                    if isinstance(values[field.name], Model):
                        values[field.name].save()
                else:
                    values[field.name] = None
            return values

        if self.pk is None:
            Signal.send(
                f"{self._table}_{When.BEFORE.name}_{Event.INSERT.name}",
                None,
                self,
            )
            obj = Table(self.__class__).insert(**get_values())
            self.__id = obj.__id
            for field in self._fields:
                setattr(self, field.name, getattr(obj, field.name))
            Signal.send(
                f"{self._table}_{When.AFTER.name}_{Event.INSERT.name}",
                None,
                self,
            )
        else:
            old_obj = Table(self.__class__).get(self.pk)
            Signal.send(
                f"{self._table}_{When.BEFORE.name}_{Event.UPDATE.name}",
                old_obj,
                self,
            )
            Table(self.__class__).where(**{self._pk.name: self.pk}).update(
                **get_values()
            )
            self.flush()
            Signal.send(
                f"{self._table}_{When.AFTER.name}_{Event.UPDATE.name}",
                old_obj,
                self,
            )

        return self

    def clear(self) -> None:
        if self.pk is not None:
            Signal.send(
                f"{self._table}_{When.BEFORE.name}_{Event.DELETE.name}", self, None
            )
            Table(self.__class__).where(**{self._pk.name: self.pk}).delete()
            self.__id = None
            Signal.send(
                f"{self._table}_{When.AFTER.name}_{Event.UPDATE.name}", self, None
            )
        for field in self._fields:
            delattr(self, field.name)

    class Meta:
        unique_together: Optional[Tuple[Tuple]] = None
        ordering: Optional[Tuple] = None
