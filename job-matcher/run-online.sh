#!/bin/bash

# ============================================
# JOB MATCHER - ONE-CLICK ONLINE STARTER
# For GitHub Codespaces
# ============================================

echo ""
echo "====================================="
echo "   JOB MATCHER - Online Setup"
echo "====================================="
echo ""

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file."
    echo ""
    echo "TIP: For smarter job matching, add your OpenAI key:"
    echo "  1. Open the .env file (click it in the file list on the left)"
    echo "  2. Replace 'sk-...' with your real key"
    echo "  3. Save the file"
    echo ""
    echo "(The app works without it too - just less accurate)"
    echo ""
fi

echo "Starting all services... (first time takes 3-5 minutes)"
echo ""
echo "When you see 'Uvicorn running' - the app is ready!"
echo "A browser tab will open automatically with your dashboard."
echo ""
echo "====================================="
echo ""

docker compose up --build
