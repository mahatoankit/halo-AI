#!/bin/bash

# HALO-AI Development Setup Script
echo "🌾 Setting up HALO-AI Crop Recommendation System"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating directory structure..."
mkdir -p logs
mkdir -p models
mkdir -p data

# Copy models if they exist in the old structure
if [ -d "../models" ] && [ "$(ls -A ../models)" ]; then
    echo "Copying existing models..."
    cp ../models/*.pkl models/ 2>/dev/null || echo "No .pkl files found in ../models"
fi

# Copy data if it exists
if [ -d "../data" ] && [ "$(ls -A ../data)" ]; then
    echo "Copying existing data..."
    cp ../data/*.csv data/ 2>/dev/null || echo "No .csv files found in ../data"
fi

echo "✅ Setup completed!"
echo ""
echo "To start the development server:"
echo "1. source venv/bin/activate"
echo "2. cd src/backend"
echo "3. python main.py"
echo ""
echo "To train models:"
echo "1. source venv/bin/activate"
echo "2. cd src/ml/training"
echo "3. python train_models.py"
echo ""
echo "To start the frontend:"
echo "Open src/frontend/index.html in your browser"
