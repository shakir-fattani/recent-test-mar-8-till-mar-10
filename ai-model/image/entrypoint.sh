#!/bin/bash
set -e

./start_all.sh
./novnc_startup.sh

# Start the HTTP server
python http_server.py >/tmp/server_logs.txt 2>&1 &

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

pip install python-multipart

# Start Streamlit
STREAMLIT_SERVER_PORT=8501 python -m streamlit run enterprise_computer_use/streamlit.py >/tmp/streamlit_stdout.log &
python enterprise_computer_use/fastapi_app.py &

echo "🎉 Computer Use Demo is ready!"
echo "🌐 Open http://localhost:8080 in your browser to begin"
echo "🌐 Open http://localhost:8000 in your API to begin"

# Keep the container running
tail -f /dev/null
