#!/bin/bash
# Start in development mode (backend + frontend separately)

# Start backend in background
echo "Starting backend on port 8000..."
python -m uvicorn backend.main:app --reload --port 8000 &
BACKEND_PID=$!

# Start frontend dev server
echo "Starting frontend dev server on port 5173..."
cd frontend && npm run dev &
FRONTEND_PID=$!

echo ""
echo "App running at:"
echo "  Frontend: http://localhost:5173"
echo "  Backend:  http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
wait
