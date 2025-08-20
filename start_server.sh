#!/bin/bash

# SportsIQ Basketball Analysis Server Startup Script

echo "🏀 Starting SportsIQ Basketball Analysis Server..."
echo "================================================="

# Activate conda environment
echo "📦 Activating conda environment 'sportsIQ'..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate sportsIQ

# Check if activation was successful
if [ "$CONDA_DEFAULT_ENV" != "sportsIQ" ]; then
    echo "❌ Failed to activate conda environment 'sportsIQ'"
    echo "Please run: conda create -n sportsIQ python=3.11"
    exit 1
fi

echo "✅ Environment activated: $CONDA_DEFAULT_ENV"

# Navigate to backend directory
cd backend

# Check if required files exist
if [ ! -f "app.py" ]; then
    echo "❌ Backend files not found. Please ensure you're in the correct directory."
    exit 1
fi

echo "🚀 Starting Flask server..."
echo "📱 iOS app should connect to: http://localhost:5000"
echo "🔗 API endpoints:"
echo "   - Health check: http://localhost:5000/health"
echo "   - Demo analysis: http://localhost:5000/analyze/demo"
echo "   - Shooting tips: http://localhost:5000/tips"
echo ""
echo "Press Ctrl+C to stop the server"
echo "================================================="

# Start the Flask server
python app.py
