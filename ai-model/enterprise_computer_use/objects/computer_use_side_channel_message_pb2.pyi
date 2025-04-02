from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ComputerUseChannelDataTypeProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    BOOLEAN: _ClassVar[ComputerUseChannelDataTypeProto]
    INT: _ClassVar[ComputerUseChannelDataTypeProto]
    FLOAT: _ClassVar[ComputerUseChannelDataTypeProto]
    FLOAT_LIST: _ClassVar[ComputerUseChannelDataTypeProto]
    STRING: _ClassVar[ComputerUseChannelDataTypeProto]
BOOLEAN: ComputerUseChannelDataTypeProto
INT: ComputerUseChannelDataTypeProto
FLOAT: ComputerUseChannelDataTypeProto
FLOAT_LIST: ComputerUseChannelDataTypeProto
STRING: ComputerUseChannelDataTypeProto

class ComputerUseBoolDataProto(_message.Message):
    __slots__ = ("val",)
    VAL_FIELD_NUMBER: _ClassVar[int]
    val: bool
    def __init__(self, val: bool = ...) -> None: ...

class ComputerUseFloatDataProto(_message.Message):
    __slots__ = ("val",)
    VAL_FIELD_NUMBER: _ClassVar[int]
    val: float
    def __init__(self, val: _Optional[float] = ...) -> None: ...

class ComputerUseFloatListDataProto(_message.Message):
    __slots__ = ("val",)
    VAL_FIELD_NUMBER: _ClassVar[int]
    val: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, val: _Optional[_Iterable[float]] = ...) -> None: ...

class ComputerUseIntDataProto(_message.Message):
    __slots__ = ("val",)
    VAL_FIELD_NUMBER: _ClassVar[int]
    val: int
    def __init__(self, val: _Optional[int] = ...) -> None: ...

class ComputerUseStringDataProto(_message.Message):
    __slots__ = ("val",)
    VAL_FIELD_NUMBER: _ClassVar[int]
    val: str
    def __init__(self, val: _Optional[str] = ...) -> None: ...

class ComputerUseBytesDataProto(_message.Message):
    __slots__ = ("val",)
    VAL_FIELD_NUMBER: _ClassVar[int]
    val: bytes
    def __init__(self, val: _Optional[bytes] = ...) -> None: ...

class ComputerUseSideChannelMessageProto(_message.Message):
    __slots__ = ("key", "store_local", "boolVal", "intVal", "floatVal", "floatListVal", "stringVal", "bytesVal")
    KEY_FIELD_NUMBER: _ClassVar[int]
    STORE_LOCAL_FIELD_NUMBER: _ClassVar[int]
    BOOLVAL_FIELD_NUMBER: _ClassVar[int]
    INTVAL_FIELD_NUMBER: _ClassVar[int]
    FLOATVAL_FIELD_NUMBER: _ClassVar[int]
    FLOATLISTVAL_FIELD_NUMBER: _ClassVar[int]
    STRINGVAL_FIELD_NUMBER: _ClassVar[int]
    BYTESVAL_FIELD_NUMBER: _ClassVar[int]
    key: str
    store_local: bool
    boolVal: ComputerUseBoolDataProto
    intVal: ComputerUseIntDataProto
    floatVal: ComputerUseFloatDataProto
    floatListVal: ComputerUseFloatListDataProto
    stringVal: ComputerUseStringDataProto
    bytesVal: ComputerUseBytesDataProto
    def __init__(self, key: _Optional[str] = ..., store_local: bool = ..., boolVal: _Optional[_Union[ComputerUseBoolDataProto, _Mapping]] = ..., intVal: _Optional[_Union[ComputerUseIntDataProto, _Mapping]] = ..., floatVal: _Optional[_Union[ComputerUseFloatDataProto, _Mapping]] = ..., floatListVal: _Optional[_Union[ComputerUseFloatListDataProto, _Mapping]] = ..., stringVal: _Optional[_Union[ComputerUseStringDataProto, _Mapping]] = ..., bytesVal: _Optional[_Union[ComputerUseBytesDataProto, _Mapping]] = ...) -> None: ...
