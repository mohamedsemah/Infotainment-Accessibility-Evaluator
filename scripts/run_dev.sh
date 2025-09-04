#!/bin/bash

# Bash script to run development environment on Unix-like systems

echo "Starting Infotainment Accessibility Evaluator Development Environment"
echo "================================================================="

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Copying from env.example..."
    cp env.example .env
    echo "Please edit .env and add your API keys before running the development environment."
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 not found. Please install Python 3.9+ and add it to PATH."
    exit 1
fi

echo "Python found: $(python3 --version)"

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "Error: Node.js not found. Please install Node.js 18+ and add it to PATH."
    exit 1
fi

echo "Node.js found: $(node --version)"

# Install backend dependencies
echo "Installing backend dependencies..."
cd backend
pip3 install -e .
if [ $? -ne 0 ]; then
    echo "Error: Failed to install backend dependencies."
    exit 1
fi
cd ..

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd frontend
npm install
if [ $? -ne 0 ]; then
    echo "Error: Failed to install frontend dependencies."
    exit 1
fi
cd ..

echo "Starting development servers..."
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop all servers."

# Function to cleanup processes on exit
cleanup() {
    echo ""
    echo "Stopping development servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    echo "Development servers stopped."
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Start backend server
echo "Starting backend server..."
cd backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start frontend server
echo "Starting frontend server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo "Development servers started successfully!"
echo "You can now access the application at http://localhost:5173"

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID
