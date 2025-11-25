#!/bin/bash
# Production Deployment Script for El Jefe Dashboard

set -e

echo "🚀 Starting Production Deployment..."

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | xargs)
else
    echo "❌ .env file not found. Copy production.env.template to .env and configure."
    exit 1
fi

# Create necessary directories
mkdir -p logs uploads backups

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run database migrations (if applicable)
# python manage.py migrate

# Start the dashboard
echo "🚀 Starting dashboard..."
python3 monitoring_dashboard.py

echo "✅ Deployment complete!"
