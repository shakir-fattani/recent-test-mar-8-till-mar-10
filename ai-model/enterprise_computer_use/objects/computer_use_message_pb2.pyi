from enterprise_computer_use.objects import computer_use_side_channel_message_pb2 as _computer_use_side_channel_message_pb2
from enterprise_computer_use.objects import computer_use_empty_message_pb2 as _computer_use_empty_message_pb2
from enterprise_computer_use.objects import computer_use_data_message_pb2 as _computer_use_data_message_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ComputerUseMessageTypeProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    EMPTY: _ClassVar[ComputerUseMessageTypeProto]
    CHANNEL: _ClassVar[ComputerUseMessageTypeProto]
    DATA: _ClassVar[ComputerUseMessageTypeProto]
EMPTY: ComputerUseMessageTypeProto
CHANNEL: ComputerUseMessageTypeProto
DATA: ComputerUseMessageTypeProto

class ComputerUseMessageHeaderProto(_message.Message):
    __slots__ = ("status", "message")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    status: int
    message: str
    def __init__(self, status: _Optional[int] = ..., message: _Optional[str] = ...) -> None: ...

class ComputerUseMessageProto(_message.Message):
    __slots__ = ("header", "emptyMsg", "sideChannelMsg", "dataMsg")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    EMPTYMSG_FIELD_NUMBER: _ClassVar[int]
    SIDECHANNELMSG_FIELD_NUMBER: _ClassVar[int]
    DATAMSG_FIELD_NUMBER: _ClassVar[int]
    header: ComputerUseMessageHeaderProto
    emptyMsg: _computer_use_empty_message_pb2.ComputerUseEmptyMessageProto
    sideChannelMsg: _computer_use_side_channel_message_pb2.ComputerUseSideChannelMessageProto
    dataMsg: _computer_use_data_message_pb2.ComputerUseDataMessageProto
    def __init__(self, header: _Optional[_Union[ComputerUseMessageHeaderProto, _Mapping]] = ..., emptyMsg: _Optional[_Union[_computer_use_empty_message_pb2.ComputerUseEmptyMessageProto, _Mapping]] = ..., sideChannelMsg: _Optional[_Union[_computer_use_side_channel_message_pb2.ComputerUseSideChannelMessageProto, _Mapping]] = ..., dataMsg: _Optional[_Union[_computer_use_data_message_pb2.ComputerUseDataMessageProto, _Mapping]] = ...) -> None: ...
