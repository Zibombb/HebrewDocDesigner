#!/bin/bash
# Start the Hebrew Book Writer application

set -e

# Check for .env file
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "Created .env from .env.example — please add your ANTHROPIC_API_KEY"
fi

# Install Python dependencies if needed
if ! python -c "import fastapi" 2>/dev/null; then
  echo "Installing Python dependencies..."
  pip install -r requirements.txt
fi

# Build frontend if dist doesn't exist or src is newer
if [ ! -d "frontend/dist" ]; then
  echo "Building frontend..."
  cd frontend
  npm install
  npm run build
  cd ..
fi

echo "Starting server on http://localhost:8000"
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
