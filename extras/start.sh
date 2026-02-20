#!/bin/bash

echo "🚀 AI Resume Generator - Quick Start Script"
echo "==========================================="
echo ""

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp backend/.env.example backend/.env
    echo "📝 Please edit backend/.env and add your ANTHROPIC_API_KEY"
    echo "   Get your key from: https://console.anthropic.com/"
    echo ""
    read -p "Press enter once you've added your API key..."
fi

# Check for Docker
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    echo "🐳 Docker detected! Starting with Docker Compose..."
    docker-compose up --build
else
    echo "🔧 Docker not found. Starting manually..."
    
    # Start backend
    echo "📦 Installing backend dependencies..."
    cd backend
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    pip install -r requirements.txt
    
    echo "🚀 Starting backend server..."
    python main.py &
    BACKEND_PID=$!
    
    cd ..
    
    # Start frontend
    echo "📦 Installing frontend dependencies..."
    cd frontend
    
    if [ ! -d "node_modules" ]; then
        npm install
    fi
    
    echo "🚀 Starting frontend server..."
    npm run dev &
    FRONTEND_PID=$!
    
    cd ..
    
    echo ""
    echo "✅ Application started!"
    echo "   Backend:  http://localhost:8000"
    echo "   Frontend: http://localhost:3000"
    echo ""
    echo "Press Ctrl+C to stop..."
    
    # Wait for Ctrl+C
    trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
    wait
fi
