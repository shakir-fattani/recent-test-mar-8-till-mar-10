#!/bin/bash
set -e

# Start the HTTP server
python http_server.py >/tmp/server_logs.txt 2>&1 &

# Start Streamlit
STREAMLIT_SERVER_PORT=8501 python -m streamlit run enterprise_computer_use/streamlit.py >/tmp/streamlit_stdout.log &

# Sleep for 2 seconds to allow Streamlit to start up
sleep 2

# Check if required ports are listening
echo "Checking required ports..."

# Check Streamlit port 8501
if netstat -tuln | grep -q ":8501 "; then
    echo "✅ Streamlit server listening on port 8501"
else
    echo "❌ Streamlit server not listening on port 8501"
    exit 1
fi

# Check HTTP server port 8080
if netstat -tuln | grep -q ":8080 "; then
    echo "✅ HTTP server listening on port 8080"
else
    echo "❌ HTTP server not listening on port 8080"
    exit 1
fi

echo "🎉 Computer Use Client is ready!"
echo "🌐 Open http://localhost:8080 in your browser to begin"

# Keep the container running
tail -f /dev/null
