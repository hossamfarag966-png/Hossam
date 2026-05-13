#!/bin/bash

# ============================================
# JOB MATCHER - ONE-CLICK STARTER
# ============================================
# Just run this script and everything works!
# ============================================

echo ""
echo "====================================="
echo "   JOB MATCHER - Starting Up..."
echo "====================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed!"
    echo ""
    echo "Please install Docker Desktop first:"
    echo "  -> Go to: https://www.docker.com/products/docker-desktop/"
    echo "  -> Download it"
    echo "  -> Install it"
    echo "  -> Open Docker Desktop and wait until it says 'Running'"
    echo "  -> Then run this script again"
    echo ""
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null 2>&1; then
    echo "ERROR: Docker is installed but not running!"
    echo ""
    echo "Please open Docker Desktop and wait until it says 'Running'"
    echo "Then run this script again."
    echo ""
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating configuration file..."
    cp .env.example .env
    echo ""
    echo "====================================="
    echo "  FIRST TIME SETUP"
    echo "====================================="
    echo ""
    echo "I created a .env file for you."
    echo ""
    echo "OPTIONAL: If you want SMART matching, you need an OpenAI key."
    echo "(The app works without it, just less accurate)"
    echo ""
    read -p "Do you have an OpenAI API key? (y/n): " has_key
    if [ "$has_key" = "y" ] || [ "$has_key" = "Y" ]; then
        read -p "Paste your OpenAI API key here: " api_key
        if [ ! -z "$api_key" ]; then
            sed -i.bak "s|OPENAI_API_KEY=sk-...|OPENAI_API_KEY=$api_key|g" .env
            rm -f .env.bak
            echo "Key saved!"
        fi
    else
        echo "No problem! The app will use basic matching."
    fi
    echo ""
    read -p "What's your email? (for daily job digest, or press Enter to skip): " email
    if [ ! -z "$email" ]; then
        sed -i.bak "s|DIGEST_EMAIL_TO=your-email@gmail.com|DIGEST_EMAIL_TO=$email|g" .env
        sed -i.bak "s|SMTP_USER=your-email@gmail.com|SMTP_USER=$email|g" .env
        rm -f .env.bak
        echo "Email saved! (You'll need to add SMTP password later for email to work)"
    fi
    echo ""
fi

echo "Starting all services... (this may take 2-3 minutes the first time)"
echo ""

# Build and start
docker compose up --build -d

echo ""
echo "====================================="
echo "  ALL DONE! Your Job Matcher is running!"
echo "====================================="
echo ""
echo "  Open your browser and go to:"
echo ""
echo "  >>> http://localhost:3000 <<<"
echo ""
echo "====================================="
echo ""
echo "  WHAT TO DO NEXT:"
echo "  1. Go to http://localhost:3000/settings"
echo "  2. Upload your CV (PDF or Word file)"
echo "  3. Set your job preferences"
echo "  4. Go back to Dashboard and click 'Fetch New Jobs'"
echo "  5. Wait 30 seconds and refresh - you'll see matched jobs!"
echo ""
echo "  TO STOP: Run ./stop.sh or: docker compose down"
echo ""
