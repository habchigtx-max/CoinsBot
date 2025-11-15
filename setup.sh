#!/bin/bash

# AliExpress Telegram Bot Setup Script
echo "Setting up AliExpress Telegram Bot..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed. Please install Python 3 first."
    exit 1
fi

# Install required packages
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# Copy environment template
if [ ! -f .env ]; then
    echo "Creating environment configuration file..."
    cp .env.example .env
    echo "✅ Environment file created! Please edit .env with your API credentials."
else
    echo "⚠️  Environment file already exists."
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit the .env file with your actual API credentials:"
echo "   - Get your Telegram Bot Token from @BotFather"
echo "   - Get your AliExpress API credentials from AliExpress Open Platform"
echo "2. Run the bot with: python3 Bot.py"
echo ""
echo "Need help? Check the README.md file for detailed instructions."
