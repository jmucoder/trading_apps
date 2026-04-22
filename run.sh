#!/bin/bash
# Trading Application Startup Script for Mac/Linux

echo ""
echo "===================================="
echo "Trading Dashboard Startup"
echo "===================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ from python.org"
    exit 1
fi

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Virtual environment created."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if requirements are installed
echo "Checking dependencies..."
pip list | grep -q streamlit
if [ $? -ne 0 ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    echo "Dependencies installed."
else
    echo "Dependencies already installed."
fi

echo ""
echo "===================================="
echo "Starting Trading Dashboard..."
echo "===================================="
echo ""
echo "The dashboard will open in your default browser."
echo "Press Ctrl+C to stop the server."
echo ""

# Run the app
streamlit run app.py
