#!/bin/bash

# Fly.io Deployment Script for Audio Analysis API
echo "🚀 Deploying Audio Analysis API to Fly.io"
echo "=========================================="

# Check if fly CLI is installed
if ! command -v fly &> /dev/null; then
    echo "❌ Fly CLI is not installed. Installing now..."
    curl -L https://fly.io/install.sh | sh
    echo "✅ Fly CLI installed. Please restart your terminal and run this script again."
    exit 1
fi

# Check if user is logged in
if ! fly auth whoami &> /dev/null; then
    echo "🔐 Please login to Fly.io..."
    fly auth login
fi

# Deploy the application
echo "📦 Deploying application..."
fly launch --no-deploy

# Deploy the application
echo "🚀 Deploying to Fly.io..."
fly deploy

# Scale to 1 instance
echo "⚖️  Scaling to 1 instance..."
fly scale count 1

# Get the app URL
echo "🌐 Getting app URL..."
APP_URL=$(fly status | grep "Hostname" | awk '{print $2}')

echo ""
echo "🎉 Deployment successful!"
echo "Your API is available at: https://$APP_URL"
echo ""
echo "📋 Test your API:"
echo "python test_deployment.py https://$APP_URL"
echo ""
echo "📖 API Documentation: https://$APP_URL"
echo "🏥 Health Check: https://$APP_URL/health"
