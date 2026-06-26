#!/bin/bash

echo "=== Cleaning up ports 8000 and 5173 ==="

# Function to kill process on a port
kill_port() {
    local port=$1
    echo "Checking port $port..."
    local pids=$(lsof -t -i:$port 2>/dev/null)
    if [ -n "$pids" ]; then
        echo "Found processes on port $port: $pids. Killing them..."
        echo "$pids" | xargs kill -9
        echo "Port $port cleared."
    else
        echo "No active processes found on port $port."
    fi
}

kill_port 8000
kill_port 5173

echo "=== Cleanup completed! ==="
