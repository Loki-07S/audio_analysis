#!/bin/bash

# Audio Analysis Model Deployment Script
# This script helps you deploy your model to various platforms

set -e

echo "🚀 Audio Analysis Model Deployment Script"
echo "=========================================="

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install git first."
    exit 1
fi

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "📁 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit: Audio Analysis Model"
fi

# Check if remote repository exists
if ! git remote get-url origin &> /dev/null; then
    echo "⚠️  No remote repository found."
    echo "Please create a repository on GitHub and add it as origin:"
    echo "git remote add origin https://github.com/yourusername/your-repo-name.git"
    echo "git push -u origin main"
    echo ""
    echo "Then run this script again."
    exit 1
fi

echo "✅ Git repository is ready!"

# Show deployment options
echo ""
echo "🎯 Choose your deployment platform:"
echo "1. Railway (Recommended - Free GPU)"
echo "2. Render (Free Tier)"
echo "3. Hugging Face Spaces (Free GPU)"
echo "4. Test locally with Docker"
echo "5. Exit"

read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo ""
        echo "🚂 Deploying to Railway..."
        echo "1. Go to https://railway.app"
        echo "2. Sign up/Login with GitHub"
        echo "3. Click 'New Project'"
        echo "4. Select 'Deploy from GitHub repo'"
        echo "5. Select this repository"
        echo "6. Railway will automatically detect the railway.json file"
        echo "7. Enable GPU in the Railway dashboard (free tier available)"
        echo ""
        echo "✅ Your app will be deployed automatically!"
        ;;
    2)
        echo ""
        echo "🎨 Deploying to Render..."
        echo "1. Go to https://render.com"
        echo "2. Sign up/Login with GitHub"
        echo "3. Click 'New +' and select 'Web Service'"
        echo "4. Connect your GitHub repository"
        echo "5. Select 'Docker' as the environment"
        echo "6. Render will use the render.yaml configuration"
        echo "7. Click 'Create Web Service'"
        echo ""
        echo "✅ Your app will be deployed automatically!"
        ;;
    3)
        echo ""
        echo "🤗 Deploying to Hugging Face Spaces..."
        echo "1. Go to https://huggingface.co"
        echo "2. Sign up/Login"
        echo "3. Click 'New Space'"
        echo "4. Choose a name and select 'Docker' as SDK"
        echo "5. Upload your code or connect GitHub"
        echo "6. Enable GPU in the Space settings"
        echo "7. Your app will be deployed automatically"
        echo ""
        echo "✅ Your app will be deployed automatically!"
        ;;
    4)
        echo ""
        echo "🐳 Testing locally with Docker..."
        
        # Check if Docker is installed
        if ! command -v docker &> /dev/null; then
            echo "❌ Docker is not installed. Please install Docker first."
            exit 1
        fi
        
        echo "Building Docker image..."
        docker build -t audio-analysis .
        
        echo "Running container..."
        docker run -d -p 8000:8000 --name audio-analysis-app audio-analysis
        
        echo "✅ App is running at http://localhost:8000"
        echo "Test with: python test_deployment.py http://localhost:8000"
        ;;
    5)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "📋 After deployment, test your API with:"
echo "python test_deployment.py https://your-app-url.com"
echo ""
echo "📖 For detailed instructions, see DEPLOYMENT.md"
echo ""
echo "�� Happy deploying!"
