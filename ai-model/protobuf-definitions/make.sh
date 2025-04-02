# GRPC-TOOLS required.

SRC_DIR=proto/enterprise_computer_use/objects
DST_DIR_P=../
PROTO_PATH=proto
PYTHON_PACKAGE=enterprise_computer_use/objects

# clean
rm -rf $DST_DIR_P/$PYTHON_PACKAGE
mkdir -p $DST_DIR_P/$PYTHON_PACKAGE

# grpc
python3 -m grpc_tools.protoc --proto_path=$PROTO_PATH --python_out=$DST_DIR_P --pyi_out=$DST_DIR_P --grpc_python_out=$DST_DIR_P $SRC_DIR/*.proto
touch $DST_DIR_P/$PYTHON_PACKAGE/__init__.py

echo "✅ Successfully generated protobuf files"
