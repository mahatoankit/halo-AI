#!/bin/bash

# HALO-AI API Server Startup Script
echo "🚀 Starting HALO-AI API Server..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if models exist
if [ ! -f "models/xgboost_model.pkl" ]; then
    echo "⚠️  No trained models found. Training models..."
    cd src/ml/training
    python train_models.py
    cd ../../..
fi

# Start the API server
echo "Starting FastAPI server..."
cd src/backend
export PYTHONPATH="../../:$PYTHONPATH"
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
