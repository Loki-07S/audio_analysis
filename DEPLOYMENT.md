# Audio Analysis Model Deployment Guide

This guide will help you deploy your audio analysis model with GPU support on free hosting platforms.

## 🚀 Quick Deploy Options

### Option 1: Railway (Recommended - Free GPU)
Railway offers free GPU instances and is the easiest to deploy.

1. **Sign up** at [railway.app](https://railway.app)
2. **Connect your GitHub repository**
3. **Deploy automatically** - Railway will detect the `railway.json` file
4. **Enable GPU** in the Railway dashboard (free tier available)

### Option 2: Render (Free Tier)
Render offers a generous free tier with GPU support.

1. **Sign up** at [render.com](https://render.com)
2. **Create a new Web Service**
3. **Connect your GitHub repository**
4. **Select Docker** as the environment
5. **Deploy** - Render will use the `render.yaml` configuration

### Option 3: Hugging Face Spaces (Free GPU)
Hugging Face Spaces offers free GPU instances for ML models.

1. **Sign up** at [huggingface.co](https://huggingface.co)
2. **Create a new Space**
3. **Select Gradio** or **Docker** as the SDK
4. **Upload your code** or connect GitHub
5. **Enable GPU** in the Space settings

## 📋 API Endpoints

Once deployed, your API will have these endpoints:

### 1. Speaking Analysis (`POST /speaking`)
Analyzes audio for fluency, grammar, and professionalism.

**Request:**
```bash
curl -X POST https://your-app.railway.app/speaking \
  -F "audio=@your_audio_file.mp3"
```

**Response:**
```json
{
  "score": 85.5,
  "report": {
    "fluency_analysis": {
      "score": 90,
      "analysis": ["Excellent speech activity", "Good rhythm consistency"]
    },
    "grammar_analysis": {
      "score": 85,
      "analysis": ["Good grammar with minor errors"],
      "errors": ["grammar error details"],
      "error_count": 2
    },
    "professionalism_analysis": {
      "score": 80,
      "analysis": ["Confident communication style"]
    }
  }
}
```

### 2. Listening Analysis (`POST /listening`)
Compares audio with provided text for similarity assessment.

**Request:**
```bash
curl -X POST https://your-app.railway.app/listening \
  -F "audio=@your_audio_file.mp3" \
  -F "text=Your reference text here"
```

**Response:**
```json
{
  "score": 88.2,
  "report": {
    "fluency_analysis": {
      "score": 85,
      "analysis": ["Good speech rate"]
    },
    "grammar_analysis": {
      "score": 90,
      "analysis": ["Excellent grammar"]
    },
    "similarity_analysis": {
      "score": 92,
      "summary": ["Perfect match with the provided script"]
    }
  }
}
```

### 3. Health Check (`GET /health`)
Check if the API is running and GPU is available.

**Request:**
```bash
curl https://your-app.railway.app/health
```

**Response:**
```json
{
  "status": "healthy",
  "message": "Audio Analysis API is running",
  "gpu_available": true
}
```

## 🔧 Environment Variables

Set these environment variables in your hosting platform:

- `PORT`: Port number (usually set automatically)
- `PYTHON_VERSION`: Python version (3.9 recommended)

## 📁 Supported Audio Formats

- WAV
- MP3
- M4A
- FLAC
- OGG

## ⚡ Performance Tips

1. **GPU Usage**: The model automatically uses GPU if available
2. **File Size**: Maximum 16MB per audio file
3. **Processing Time**: Typically 10-30 seconds depending on audio length
4. **Concurrent Requests**: Limited to 1 worker for GPU memory efficiency

## 🐛 Troubleshooting

### Common Issues:

1. **GPU Not Available**
   - Check `/health` endpoint
   - Verify GPU is enabled in hosting platform
   - Model will fall back to CPU if GPU unavailable

2. **Memory Issues**
   - Reduce audio file size
   - Check hosting platform memory limits
   - Consider upgrading to paid tier for more memory

3. **Timeout Errors**
   - Audio files should be under 5 minutes
   - Check network connectivity
   - Verify audio format is supported

### Debug Commands:

```bash
# Test locally
python app.py

# Test with Docker
docker build -t audio-analysis .
docker run -p 8000:8000 audio-analysis

# Test API endpoints
curl -X POST http://localhost:8000/speaking -F "audio=@test.mp3"
```

## 🔒 Security Considerations

1. **File Upload Limits**: 16MB maximum
2. **File Type Validation**: Only audio files allowed
3. **Temporary Files**: Automatically cleaned up after processing
4. **No Data Storage**: Audio files are not stored permanently

## 📊 Monitoring

Monitor your deployment using:

1. **Health Checks**: `/health` endpoint
2. **Logs**: Check hosting platform logs
3. **Performance**: Monitor response times and error rates
4. **GPU Usage**: Check GPU availability and utilization

## 🆘 Support

If you encounter issues:

1. Check the `/health` endpoint
2. Review hosting platform logs
3. Verify audio file format and size
4. Test with a simple audio file first
5. Check GPU availability in your hosting platform

## 🎯 Next Steps

After deployment:

1. **Test all endpoints** with sample audio files
2. **Monitor performance** and adjust resources if needed
3. **Set up monitoring** for production use
4. **Consider scaling** if you need higher throughput
5. **Add authentication** if needed for production use
