import json
import re
from datetime import date, datetime, time, timedelta
from typing import Any, Dict, List, Tuple, Union

from .constant import DataType


class FMeta(type):
    def __new__(cls, name: str, bases: tuple, attrs: dict) -> type:
        new_class = super().__new__(cls, name, bases, attrs)
        if name != "F":
            mapping = getattr(eval("F"), "mapping")
            mapping[name] = (attrs["default"], attrs["returntype"])
            setattr(eval("F"), "mapping", mapping)
        return new_class


class ReturnType:
    def __init__(self, value: Union[int, DataType]) -> None:
        self.value = value


class F(metaclass=FMeta):
    mapping: Dict[str, Tuple[str, ReturnType]] = {"F": ("%s", ReturnType(0))}
    returntype: ReturnType

    @staticmethod
    def update(mapping: Dict[str, str]) -> None:
        F.mapping.update(mapping)

    def __init__(self, *args) -> None:
        def transform(value: Any) -> str:
            if hasattr(value, "pk"):
                value = value.pk
            if isinstance(value, str):
                return f"\"'{value}'\""
            elif value is None:
                return "null"
            elif isinstance(value, bool):
                return str(int(value))
            elif isinstance(value, (int, float)):
                return str(value)
            elif isinstance(value, (date, time, datetime)):
                return f"\"'{value.strftime('%Y-%m-%d %H:%M:%S')}'\""
            elif isinstance(value, F):
                return value._str
            return value

        name = self.__class__.__name__
        if name == "F":
            if isinstance(args[0], str):
                self._str = f'["F","`{args[0]}`"]'
                self.returntype = ReturnType(0)
            else:
                self._str = args[0]._str
                self.returntype = args[0].returntype
        else:
            self._str = f'["{name}",{",".join(transform(x) for x in args)}]'

    def gettype(self, fields: List[Any]) -> DataType:
        def decode(obj, fields):
            if not isinstance(obj, list):
                matched = re.match("`(\\w+)`", obj)
                if matched is not None:
                    name, *fk = matched.group(1).split("__", 1)
                    for field in fields:
                        if field.name == name:
                            if fk:
                                return decode(f"`{fk[0]}`", field.to._fields)
                            return field.datatype
                return obj
            returntype = self.mapping[obj[0]][1]
            if isinstance(returntype.value, DataType):
                return returntype.value
            return decode(obj[1:][returntype.value], fields)

        data = json.loads(self._str)
        return decode(data, fields)

    def __str__(self) -> str:
        def decode(obj):
            if not isinstance(obj, list):
                return obj
            args = [decode(arg) for arg in obj[1:]]
            pattern = self.mapping[obj[0]][0]
            argc = pattern.count("%s")
            if len(args) >= argc:
                count = len(args) - argc
                if pattern.find("...") >= 0:
                    pattern = pattern.replace("...", ",%s" * count)
                if pattern.find("?") >= 0:
                    pattern = pattern.replace("?", ",%s", count).replace("?", "")
            return pattern % tuple(args)

        data = json.loads(self._str)
        return decode(data)

    def __add__(self, obj: Any) -> "F":
        if isinstance(obj, timedelta):
            return Date_Add(self, obj.seconds, obj.days)
        return Add(self, obj)

    def __sub__(self, obj: Any) -> "F":
        if isinstance(obj, timedelta):
            return Date_Sub(self, obj.seconds, obj.days)
        return Sub(self, obj)

    def __mul__(self, obj: Any) -> "F":
        return Mul(self, obj)

    def __truediv__(self, obj: Any) -> "F":
        return Div(self, obj)

    def __floordiv__(self, obj: Any) -> "F":
        return Floor(Div(self, obj))

    def __mod__(self, obj: Any) -> "F":
        return Mod(self, obj)

    def __eq__(self, obj: Any) -> "F":
        if obj is None:
            return Isnull(self)
        return Equal(self, obj)

    def __ne__(self, obj: Any) -> "F":
        if obj is None:
            return Not(Isnull(self))
        return Not(Equal(self, obj))

    def __gt__(self, obj: Any) -> "F":
        return Gt(self, obj)

    def __lt__(self, obj: Any) -> "F":
        return Lt(self, obj)

    def __ge__(self, obj: Any) -> "F":
        return Ge(self, obj)

    def __le__(self, obj: Any) -> "F":
        return Le(self, obj)

    def __pos__(self) -> "F":
        return F(self)

    def __neg__(self) -> "F":
        return Neg(self)

    def __abs__(self) -> "F":
        return Abs(self)

    def __ceil__(self) -> "F":
        return Ceil(self)

    def __floor__(self) -> "F":
        return Floor(self)

    def __trunc__(self) -> "F":
        return Round(self)

    def __round__(self, n: int = 0) -> "F":
        return Round(self, n)

    def __invert__(self) -> "F":
        return Not(self)

    def __and__(self, obj: Any) -> "F":
        return And(self, obj)

    def __or__(self, obj: Any) -> "F":
        return Or(self, obj)


class Add(F):
    default: str = "(%s+%s)"
    returntype: ReturnType = ReturnType(DataType.Float)


class Sub(F):
    default: str = "(%s-%s)"
    returntype: ReturnType = ReturnType(DataType.Float)


class Mul(F):
    default: str = "(%s*%s)"
    returntype: ReturnType = ReturnType(DataType.Float)


class Div(F):
    default: str = "((%s+0.0)/%s)"
    returntype: ReturnType = ReturnType(DataType.Float)


class Mod(F):
    default: str = "(%s%%%s)"
    returntype: ReturnType = ReturnType(DataType.Integer)


class Date_Format(F):
    default: str = "DATE_FORMAT(%s,%s)"
    returntype: ReturnType = ReturnType(DataType.DateTime)


class Year(F):
    default: str = "CAST(DATE_FORMAT(%s,'%%Y') AS SIGNED INT)"
    returntype: ReturnType = ReturnType(DataType.Integer)


class Month(F):
    default: str = "CAST(DATE_FORMAT(%s,'%%m') AS SIGNED INT)"
    returntype: ReturnType = ReturnType(DataType.Integer)


class Day(F):
    default: str = "CAST(DATE_FORMAT(%s,'%%d') AS SIGNED INT)"
    returntype: ReturnType = ReturnType(DataType.Integer)


class Hour(F):
    default: str = "CAST(DATE_FORMAT(%s,'%%H') AS SIGNED INT)"
    returntype: ReturnType = ReturnType(DataType.Integer)


class Minute(F):
    default: str = "CAST(DATE_FORMAT(%s,'%%M') AS SIGNED INT)"
    returntype: ReturnType = ReturnType(DataType.Integer)


class Second(F):
    default: str = "CAST(DATE_FORMAT(%s,'%%S') AS SIGNED INT)"
    returntype: ReturnType = ReturnType(DataType.Integer)


class Datediff(F):
    default: str = "DATEDIFF(%s,%s)"
    returntype: ReturnType = ReturnType(DataType.Integer)


class Date_Add(F):
    default: str = "ADDDATE(ADDTIME(%s,%s),%s)"
    returntype: ReturnType = ReturnType(0)


class Date_Sub(F):
    default: str = "SUBDATE(ADDTIME(%s,%s),%s)"
    returntype: ReturnType = ReturnType(0)


class Int(F):
    default: str = "CAST(CAST(%s AS CHAR) AS SIGNED INT)"
    returntype: ReturnType = ReturnType(DataType.Integer)


class Float(F):
    default: str = "CAST(%s AS FLOAT)"
    returntype: ReturnType = ReturnType(DataType.Float)


class Str(F):
    default: str = "CAST(%s AS CHAR)"
    returntype: ReturnType = ReturnType(DataType.String)


class Concat(F):
    default: str = "CONCAT(%s,%s...)"
    returntype: ReturnType = ReturnType(DataType.String)


class Length(F):
    default: str = "LENGTH(%s)"
    returntype: ReturnType = ReturnType(DataType.Integer)


class Upper(F):
    default: str = "UPPER(%s)"
    returntype: ReturnType = ReturnType(DataType.String)


class Lower(F):
    default: str = "LOWER(%s)"
    returntype: ReturnType = ReturnType(DataType.String)


class Neg(F):
    default: str = "(-%s)"
    returntype: ReturnType = ReturnType(0)


class Abs(F):
    default: str = "ABS(%s)"
    returntype: ReturnType = ReturnType(0)


class Ceil(F):
    default: str = "CEIL(%s)"
    returntype: ReturnType = ReturnType(DataType.Integer)


class Floor(F):
    default: str = "FLOOR(%s)"
    returntype: ReturnType = ReturnType(DataType.Integer)


class Round(F):
    default: str = "ROUND(%s?)"
    returntype: ReturnType = ReturnType(DataType.Float)


class Equal(F):
    default: str = "%s=%s"
    returntype: ReturnType = ReturnType(DataType.Boolean)


class Gt(F):
    default: str = "%s>%s"
    returntype: ReturnType = ReturnType(DataType.Boolean)


class Lt(F):
    default: str = "%s<%s"
    returntype: ReturnType = ReturnType(DataType.Boolean)


class Ge(F):
    default: str = "%s>=%s"
    returntype: ReturnType = ReturnType(DataType.Boolean)


class Le(F):
    default: str = "%s<=%s"
    returntype: ReturnType = ReturnType(DataType.Boolean)


class In(F):
    default: str = "%s IN (%s...)"
    returntype: ReturnType = ReturnType(DataType.Boolean)


class Isnull(F):
    default: str = "%s IS NULL"
    returntype: ReturnType = ReturnType(DataType.Boolean)


class And(F):
    default: str = "(%s AND %s)"
    returntype: ReturnType = ReturnType(DataType.Boolean)


class Or(F):
    default: str = "(%s OR %s)"
    returntype: ReturnType = ReturnType(DataType.Boolean)


class Not(F):
    default: str = "(NOT %s)"
    returntype: ReturnType = ReturnType(DataType.Boolean)


class Count(F):
    default: str = "COUNT(%s)"
    returntype: ReturnType = ReturnType(DataType.Integer)


class Max(F):
    default: str = "MAX(%s)"
    returntype: ReturnType = ReturnType(0)


class Min(F):
    default: str = "MIN(%s)"
    returntype: ReturnType = ReturnType(0)


class Avg(F):
    default: str = "AVG(%s)"
    returntype: ReturnType = ReturnType(0)


class Sum(F):
    default: str = "sum(%s)"
    returntype: ReturnType = ReturnType(0)
