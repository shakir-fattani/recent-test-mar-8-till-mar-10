# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: enterprise_computer_use/objects/computer_use_side_channel_message.proto
# Protobuf Python Version: 5.29.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    0,
    '',
    'enterprise_computer_use/objects/computer_use_side_channel_message.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\nGenterprise_computer_use/objects/computer_use_side_channel_message.proto\x12\x14\x63omputer_use_objects\"\'\n\x18\x43omputerUseBoolDataProto\x12\x0b\n\x03val\x18\x01 \x01(\x08\"(\n\x19\x43omputerUseFloatDataProto\x12\x0b\n\x03val\x18\x01 \x01(\x02\",\n\x1d\x43omputerUseFloatListDataProto\x12\x0b\n\x03val\x18\x01 \x03(\x02\"&\n\x17\x43omputerUseIntDataProto\x12\x0b\n\x03val\x18\x01 \x01(\x05\")\n\x1a\x43omputerUseStringDataProto\x12\x0b\n\x03val\x18\x01 \x01(\t\"(\n\x19\x43omputerUseBytesDataProto\x12\x0b\n\x03val\x18\x01 \x01(\x0c\"\xf0\x03\n\"ComputerUseSideChannelMessageProto\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x13\n\x0bstore_local\x18\x02 \x01(\x08\x12\x41\n\x07\x62oolVal\x18\x03 \x01(\x0b\x32..computer_use_objects.ComputerUseBoolDataProtoH\x00\x12?\n\x06intVal\x18\x04 \x01(\x0b\x32-.computer_use_objects.ComputerUseIntDataProtoH\x00\x12\x43\n\x08\x66loatVal\x18\x05 \x01(\x0b\x32/.computer_use_objects.ComputerUseFloatDataProtoH\x00\x12K\n\x0c\x66loatListVal\x18\x06 \x01(\x0b\x32\x33.computer_use_objects.ComputerUseFloatListDataProtoH\x00\x12\x45\n\tstringVal\x18\x07 \x01(\x0b\x32\x30.computer_use_objects.ComputerUseStringDataProtoH\x00\x12\x43\n\x08\x62ytesVal\x18\x08 \x01(\x0b\x32/.computer_use_objects.ComputerUseBytesDataProtoH\x00\x42\x06\n\x04\x64\x61ta*^\n\x1f\x43omputerUseChannelDataTypeProto\x12\x0b\n\x07\x42OOLEAN\x10\x00\x12\x07\n\x03INT\x10\x01\x12\t\n\x05\x46LOAT\x10\x02\x12\x0e\n\nFLOAT_LIST\x10\x03\x12\n\n\x06STRING\x10\x04\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'enterprise_computer_use.objects.computer_use_side_channel_message_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_COMPUTERUSECHANNELDATATYPEPROTO']._serialized_start=850
  _globals['_COMPUTERUSECHANNELDATATYPEPROTO']._serialized_end=944
  _globals['_COMPUTERUSEBOOLDATAPROTO']._serialized_start=97
  _globals['_COMPUTERUSEBOOLDATAPROTO']._serialized_end=136
  _globals['_COMPUTERUSEFLOATDATAPROTO']._serialized_start=138
  _globals['_COMPUTERUSEFLOATDATAPROTO']._serialized_end=178
  _globals['_COMPUTERUSEFLOATLISTDATAPROTO']._serialized_start=180
  _globals['_COMPUTERUSEFLOATLISTDATAPROTO']._serialized_end=224
  _globals['_COMPUTERUSEINTDATAPROTO']._serialized_start=226
  _globals['_COMPUTERUSEINTDATAPROTO']._serialized_end=264
  _globals['_COMPUTERUSESTRINGDATAPROTO']._serialized_start=266
  _globals['_COMPUTERUSESTRINGDATAPROTO']._serialized_end=307
  _globals['_COMPUTERUSEBYTESDATAPROTO']._serialized_start=309
  _globals['_COMPUTERUSEBYTESDATAPROTO']._serialized_end=349
  _globals['_COMPUTERUSESIDECHANNELMESSAGEPROTO']._serialized_start=352
  _globals['_COMPUTERUSESIDECHANNELMESSAGEPROTO']._serialized_end=848
# @@protoc_insertion_point(module_scope)
