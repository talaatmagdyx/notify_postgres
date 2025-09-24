#!/bin/bash

# Data Generation Script for PostgreSQL Notification System

echo "🚀 PostgreSQL Data Generator"
echo "============================="

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "🔧 Activating virtual environment..."
    source .venv/bin/activate
fi

echo ""
echo "📊 Data Generation Options:"
echo "1. Quick generate (20 interactions)"
echo "2. Generate realistic scenario (20 interactions)"
echo "3. Generate large batch (50 interactions)"
echo "4. Generate WhatsApp only (15 interactions)"
echo "5. Generate Twitter only (10 interactions)"
echo "6. Clear data and generate fresh (20 interactions)"
echo "7. Interactive data generator"
echo "8. Exit"
echo ""

read -p "Select option (1-8): " choice

case $choice in
    1)
        echo "🔄 Quick generating 20 interactions..."
        python quick_generate.py
        ;;
    2)
        echo "🎭 Generating realistic scenario..."
        python generate_data.py
        echo "3" | python generate_data.py
        ;;
    3)
        echo "🔄 Generating large batch..."
        echo "2" | python generate_data.py
        ;;
    4)
        echo "📱 Generating WhatsApp interactions..."
        echo "4" | python generate_data.py
        ;;
    5)
        echo "🐦 Generating Twitter interactions..."
        echo "5" | python generate_data.py
        ;;
    6)
        echo "🧹 Clearing and generating fresh data..."
        python reset_data.py
        ;;
    7)
        echo "🎮 Starting interactive generator..."
        python generate_data.py
        ;;
    8)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid option. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "✅ Data generation completed!"
echo "📱 Check your React app at http://localhost:3000"
echo "🔧 Backend API at http://localhost:5001"
