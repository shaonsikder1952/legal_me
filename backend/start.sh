#!/bin/bash

# Install emergentintegrations from custom index
echo "Installing emergentintegrations..."
pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/

# Start uvicorn server
echo "Starting FastAPI server..."
PORT=${PORT:-8001}
uvicorn server:app --host 0.0.0.0 --port $PORT
