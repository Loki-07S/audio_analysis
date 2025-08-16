#!/bin/bash

# 🚀 Render Deployment Script for Audio Analysis API
# This script helps you prepare and deploy on Render

echo "🎯 Audio Analysis API - Render Deployment"
echo "========================================="

# Check if required files exist
echo "📋 Checking required files..."

required_files=("app.py" "audio_analysis.py" "requirements.txt" "render.yaml" "runtime.txt")

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file found"
    else
        echo "❌ $file missing - please create it first"
        exit 1
    fi
done

echo ""
echo "🎉 All required files are present!"
echo ""

# Display deployment steps
echo "📚 Render Deployment Steps:"
echo "============================"
echo ""
echo "1. 🚀 Go to: https://render.com"
echo "2. 📝 Click 'Get Started' and sign up"
echo "3. 🔗 Connect your GitHub account"
echo "4. ➕ Click 'New +' → 'Web Service'"
echo "5. 📁 Connect your repository:"
echo "   - Select: audio-analysis-model"
echo "   - Click 'Connect'"
echo "6. ⚙️  Configure service:"
echo "   - Name: audio-analysis-api"
echo "   - Runtime: Python 3"
echo "   - Build Command: pip install -r requirements.txt"
echo "   - Start Command: python app.py"
echo "7. 🔧 Add environment variables:"
echo "   - PORT: 10000"
echo "   - MAX_CONTENT_LENGTH: 16777216"
echo "   - PYTHON_VERSION: 3.9.16"
echo "8. 🚀 Click 'Create Web Service'"
echo "9. ⏳ Wait for build (5-10 minutes)"
echo "10. 🧪 Test your API endpoints"
echo ""

# Check if git is initialized
if [ -d ".git" ]; then
    echo "✅ Git repository detected"
    echo "🌐 Your repository URL: $(git remote get-url origin)"
    echo ""
    echo "💡 Pro tip: Push your changes to trigger auto-deployment!"
else
    echo "⚠️  Git repository not detected"
    echo "💡 Consider initializing git for easier deployment"
fi

echo ""
echo "🔧 Optimization Applied:"
echo "======================="
echo "✅ Whisper model: tiny (39MB) for 512MB RAM"
echo "✅ CPU-optimized code (no GPU required)"
echo "✅ Memory management for free tier"
echo "✅ Auto-deployment from GitHub"
echo "✅ SSL/HTTPS included automatically"
echo ""

echo "📖 For detailed instructions, see: RENDER_DEPLOYMENT.md"
echo "🎯 Your API will be available at: https://your-service-name.onrender.com"
echo ""
echo "🚀 Happy deploying on Render!"
