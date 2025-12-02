#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Server Configuration ---
# You can override these variables by setting them in your environment.
# Example: PORT=8080 WORKERS=8 ./start.sh

# The port the server will listen on.
PORT=${PORT:-8000}

# The number of worker processes for handling requests.
# Note: --workers is not compatible with --reload.
WORKERS=${WORKERS:-2}

# The directory to store log files.
LOG_DIR="logs"

# The path to the log file.
LOG_FILE="$LOG_DIR/server.log"

# --- End Configuration ---


# Create the log directory if it doesn't exist.
echo "Ensuring log directory exists at '$LOG_DIR'..."
mkdir -p "$LOG_DIR"
echo "Log directory is ready."

echo "Starting server..."
echo "Port: $PORT"
echo "Log file: $LOG_FILE"

# --- Server Start Command ---
# The --reload flag is great for development as it automatically restarts
# the server when code changes are detected.
# For production, you should comment out the development line and use the
# production line, which utilizes multiple workers for better performance.

# # Development:
# echo "Running in development mode with --reload."
# exec uvicorn main:app --host 0.0.0.0 --port "$PORT" --reload

# Production:
echo "Running in production mode with $WORKERS workers."
exec uvicorn main:app --host 0.0.0.0 --port "$PORT" --workers "$WORKERS"  2>&1 | tee $LOG_FILE #&
