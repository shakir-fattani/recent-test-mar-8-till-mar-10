#!/bin/bash
set -e

./start_all.sh
./novnc_startup.sh

# Start the gRPC server
python grpc_server.py >/tmp/grpc_server.log 2>&1 &
GRPC_PID=$!

# Wait a moment to check if gRPC server started successfully
sleep 2
if ps -p $GRPC_PID >/dev/null; then
    echo "🚀 gRPC server started successfully"
else
    echo "💥 Failed to start gRPC server"
    echo "Error logs:"
    cat /tmp/grpc_server.log
    exit 1
fi

# Check if required ports are listening
echo "Checking required ports..."

# Check gRPC port 50051
if netstat -tuln | grep -q ":50051 "; then
    echo "✅ gRPC server listening on port 50051"
else
    echo "❌ gRPC server not listening on port 50051"
    exit 1
fi

# Check VNC port 5900
if netstat -tuln | grep -q ":5900 "; then
    echo "✅ VNC server listening on port 5900"
else
    echo "❌ VNC server not listening on port 5900"
    exit 1
fi

# Check noVNC port 6080
if netstat -tuln | grep -q ":6080 "; then
    echo "✅ noVNC server listening on port 6080"
else
    echo "❌ noVNC server not listening on port 6080"
    exit 1
fi

echo "🎉 Computer Use Server is ready!"

# Keep the container running
tail -f /dev/null
