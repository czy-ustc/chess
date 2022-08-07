import json
from typing import Any, Callable, Dict, List, Optional, Tuple

from .constant import ON_DELETE, DataType


class Validator:
    @classmethod
    def validate(cls, field: "Field", value: Any) -> Any:
        return NotImplemented

    @classmethod
    def raises(self) -> None:
        raise ValueError


class DefaultValidator(Validator):
    @classmethod
    def validate(cls, field: "Field", value: Any) -> Any:
        if value is None:
            if field.default is not None:
                if not callable(field.default):
                    value = field.default
                else:
                    value = field.default()
        return value


class NotNullValidator(Validator):
    @classmethod
    def validate(cls, field: "Field", value: Any) -> Any:
        if value is None and not field.null:
            cls.raises()
        return value


class ForeignKeyValidator(Validator):
    @classmethod
    def validate(cls, field: "Field", value: Any) -> Any:
        if (
            value is not None
            and isinstance(field, ForeignKey)
            and isinstance(value, field.to)
        ):
            value = getattr(value, field.to_field)
        return value


class DataTypeValidator(Validator):
    @classmethod
    def validate(cls, field: "Field", value: Any) -> Any:
        if value is not None and not isinstance(value, field.datatype.value):
            try:
                return field.datatype.value(value)
            except ValueError:
                cls.raises()
        return value


class MaxLengthValidator(Validator):
    @classmethod
    def validate(cls, field: "Field", value: Any) -> Any:
        if (
            value is not None
            and field.max_length is not None
            and len(value) > field.max_length
        ):
            cls.raises()
        return value


class Field:
    datatype: DataType
    validators: List[Validator]

    def __init__(
        self,
        primary_key: bool = False,
        unique: bool = False,
        null: bool = False,
        default: Optional[Any] = None,
    ) -> None:
        self.primary_key = primary_key
        self.default = default
        self.config = {
            "unique": unique,
            "null": null,
        }
        self.constraint()
        self._ancestors = ()

    def constraint(self) -> None:
        if self.primary_key:
            self.null = False

    def __getattr__(self, key: str) -> Any:
        return self.config.get(key, None)

    def load(self, value: Any) -> Any:
        return value

    def dump(self, value: Any) -> Any:
        for validator in self.validators:
            value = validator.validate(self, value)
        return value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, n: str):
        self._name = n


class CharField(Field):
    datatype: DataType = DataType.String
    validators: List[Validator] = [
        DefaultValidator,
        NotNullValidator,
        DataTypeValidator,
        MaxLengthValidator,
    ]

    def __init__(
        self,
        max_length: Optional[int] = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.config["max_length"] = max_length


class IntegerField(Field):
    datatype: DataType = DataType.Integer
    validators: List[Validator] = [
        DefaultValidator,
        NotNullValidator,
        DataTypeValidator,
    ]

    def __init__(
        self,
        autoincrement: bool = False,
        choices: Optional[Tuple[Tuple[Any, Any]]] = None,
        *args,
        **kwargs,
    ) -> None:
        self.autoincrement = autoincrement
        super().__init__(*args, **kwargs)
        self.config["choices"] = choices

    def constraint(self) -> None:
        if self.autoincrement:
            self.null = True

    def load(self, value: Any) -> Any:
        if value is not None and self.choices:
            value = dict(self.choices)[value]
        return value

    def dump(self, value: Any) -> Any:
        if value is not None and self.choices:
            value = {v: k for k, v in self.choices}[value]
        return super().dump(value)


class FloatField(Field):
    datatype: DataType = DataType.Float
    validators: List[Validator] = [
        DefaultValidator,
        NotNullValidator,
        DataTypeValidator,
    ]


class BooleanField(Field):
    datatype: DataType = DataType.Boolean
    validators: List[Validator] = [
        DefaultValidator,
        NotNullValidator,
        DataTypeValidator,
    ]


class DateField(Field):
    datatype: DataType = DataType.Date
    validators: List[Validator] = [
        DefaultValidator,
        NotNullValidator,
        DataTypeValidator,
    ]


class TimeField(Field):
    datatype: DataType = DataType.Time
    validators: List[Validator] = [
        DefaultValidator,
        NotNullValidator,
        DataTypeValidator,
    ]


class DateTimeField(Field):
    datatype: DataType = DataType.DateTime
    validators: List[Validator] = [
        DefaultValidator,
        NotNullValidator,
        DataTypeValidator,
    ]


class ForeignKey(Field):
    validators: List[Validator] = [
        DefaultValidator,
        NotNullValidator,
        ForeignKeyValidator,
        DataTypeValidator,
    ]

    def __init__(
        self,
        to: Any,
        to_field: Optional[str] = None,
        related_name: Optional[str] = None,
        on_delete: ON_DELETE = ON_DELETE.CASCADE,
        on_delete_set: Optional[Any] = None,
        *args,
        **kwargs,
    ) -> None:
        self.to = to
        self.to_field = to_field or to._pk.name
        self.related_name = related_name
        self.on_delete = on_delete
        self.on_delete_set = on_delete_set
        super().__init__(*args, **kwargs)

    def constraint(self) -> None:
        if self.on_delete == ON_DELETE.SET_DEFAULT:
            self.on_delete_set = self.default
        if self.on_delete_set is not None:
            self.on_delete = ON_DELETE.SET

    def validate(self, value: Any) -> Any:
        return super().validate(value)

    def convert(self, field: Field):
        self.config = {**field.config, **self.config}
        self.datatype = field.datatype
        self.validators += [
            validator
            for validator in field.validators
            if validator not in self.validators
        ]


class ManyToManyField(ForeignKey):
    def __init__(
        self,
        to: Any,
        extras: Optional[Dict[str, Field]] = None,
        *args,
        **kwargs,
    ) -> None:
        self.extras = extras or {}
        super().__init__(to, *args, **kwargs)


class StorageClass:
    def __init__(
        self,
        describe: Callable,
        decoder: Optional[Callable] = None,
        encoder: Optional[Callable] = None,
    ) -> None:
        self._describe = describe
        self._decoder = decoder
        self._encoder = encoder

    def decode(self, value: Any, field: Optional[Field] = None) -> Any:
        if value is None:
            return value
        if field is not None:
            value = field.load(value)
        if self._decoder is not None:
            value = self._decoder(value)
        return value

    def encode(self, value: Any, field: Optional[Field] = None) -> Any:
        if field is not None:
            value = field.dump(value)
        if self._encoder is not None:
            value = self._encoder(value)
        return json.dumps(value)

    @property
    def describe(self) -> Callable:
        return self._describe
