#!/bin/bash

# 🚀 Hugging Face Spaces Deployment Script
# This script helps you prepare and deploy your Audio Analysis API

echo "🎯 Audio Analysis API - Hugging Face Spaces Deployment"
echo "======================================================"

# Check if required files exist
echo "📋 Checking required files..."

required_files=("app.py" "audio_analysis.py" "requirements.txt" "Dockerfile" ".dockerignore")

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
echo "📚 Next Steps:"
echo "=============="
echo ""
echo "1. 🚀 Go to: https://huggingface.co/spaces"
echo "2. 📝 Click 'Create new Space'"
echo "3. ⚙️  Configure your Space:"
echo "   - Owner: Your username"
echo "   - Space name: audio-analysis-api"
echo "   - SDK: Docker"
echo "   - Hardware: GPU (T4 - Free)"
echo "4. 🔗 Connect your repository"
echo "5. 🏗️  Click 'Create Space'"
echo "6. ⏳ Wait for build (5-10 minutes)"
echo "7. 🧪 Test your API endpoints"
echo ""

# Check if git is initialized
if [ -d ".git" ]; then
    echo "✅ Git repository detected"
    echo "🌐 Your repository URL: $(git remote get-url origin)"
else
    echo "⚠️  Git repository not detected"
    echo "💡 Consider initializing git for easier deployment"
fi

echo ""
echo "🔧 Optimization Applied:"
echo "======================="
echo "✅ Whisper model: tiny (39MB) instead of large (1.5GB)"
echo "✅ GPU memory management: 80% limit to prevent OOM"
echo "✅ Automatic memory cleanup after each inference"
echo "✅ CPU fallback if GPU fails"
echo "✅ Docker optimization for faster builds"
echo ""

echo "📖 For detailed instructions, see: DEPLOYMENT_HF.md"
echo "🎯 Your API will be available at: https://your-username-audio-analysis-api.hf.space"
echo ""
echo "�� Happy deploying!"
