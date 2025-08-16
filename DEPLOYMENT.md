# Audio Analysis Model Deployment Guide

This guide will help you deploy your audio analysis model with GPU support on hosting platforms that support large Docker images.

## 🚀 **Recommended Hosting Platforms (Support Large Images)**

### **Option 1: Fly.io (Recommended - Best Free Tier)**
Fly.io offers the most generous free tier and supports large images.

**Free Tier Includes:**
- ✅ **3 shared-cpu-1x 256mb VMs** (free forever)
- ✅ **3GB persistent volume storage** (free forever)
- ✅ **160GB outbound data transfer** (free forever)
- ✅ **No image size limits** for free tier
- ✅ **Global edge deployment**

**Deployment Steps:**
1. **Install Fly CLI**: `curl -L https://fly.io/install.sh | sh`
2. **Sign up** at [fly.io](https://fly.io)
3. **Login**: `fly auth login`
4. **Deploy**: `fly launch` (in your project directory)
5. **Scale**: `fly scale count 1`

### **Option 2: Heroku (Paid but Reliable)**
Heroku supports large images and has good reliability.

**Pricing:**
- **Basic Dyno**: $7/month (supports large images)
- **Standard Dyno**: $25/month (better performance)

**Deployment Steps:**
1. **Sign up** at [heroku.com](https://heroku.com)
2. **Install Heroku CLI**
3. **Login**: `heroku login`
4. **Create app**: `heroku create your-app-name`
5. **Deploy**: `git push heroku main`

### **Option 3: Google Cloud Run (Pay-per-use)**
Google Cloud Run has no image size limits and pay-per-use pricing.

**Pricing:**
- **Free tier**: 2 million requests/month
- **Pay-per-use**: ~$0.00002400 per 100ms

**Deployment Steps:**
1. **Set up Google Cloud Project**
2. **Enable Cloud Run API**
3. **Deploy**: `gcloud run deploy --source .`

### **Option 4: Railway (Paid Plan)**
Railway's paid plan supports larger images.

**Pricing:**
- **Pro Plan**: $20/month (supports large images)
- **Team Plan**: $40/month

## 📋 **API Endpoints**

Once deployed, your API will have these endpoints:

### 1. Speaking Analysis (`POST /speaking`)
Analyzes audio for fluency, grammar, and professionalism.

**Request:**
```bash
curl -X POST https://your-app.fly.dev/speaking \
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
curl -X POST https://your-app.fly.dev/listening \
  -F "audio=@your_audio_file.mp3" \
  -F "text=Your reference text here"
```

### 3. Health Check (`GET /health`)
Check if the API is running and GPU is available.

**Request:**
```bash
curl https://your-app.fly.dev/health
```

## 🔧 **Environment Variables**

Set these environment variables in your hosting platform:

- `PORT`: Port number (usually set automatically)
- `PYTHON_VERSION`: Python version (3.9 recommended)

## 📁 **Supported Audio Formats**

- WAV
- MP3
- M4A
- FLAC
- OGG

## ⚡ **Performance Tips**

1. **GPU Usage**: The model automatically uses GPU if available
2. **File Size**: Maximum 16MB per audio file
3. **Processing Time**: Typically 10-30 seconds depending on audio length
4. **Concurrent Requests**: Limited to 1 worker for GPU memory efficiency

## 🐛 **Troubleshooting**

### Common Issues:

1. **Image Size Too Large**
   - Use Fly.io or Heroku (no size limits)
   - Consider paid Railway plan
   - Use Google Cloud Run

2. **Memory Issues**
   - Increase memory allocation
   - Reduce audio file size
   - Check hosting platform memory limits

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

## 🔒 **Security Considerations**

1. **File Upload Limits**: 16MB maximum
2. **File Type Validation**: Only audio files allowed
3. **Temporary Files**: Automatically cleaned up after processing
4. **No Data Storage**: Audio files are not stored permanently

## 📊 **Monitoring**

Monitor your deployment using:

1. **Health Checks**: `/health` endpoint
2. **Logs**: Check hosting platform logs
3. **Performance**: Monitor response times and error rates
4. **GPU Usage**: Check GPU availability and utilization

## 🆘 **Support**

If you encounter issues:

1. Check the `/health` endpoint
2. Review hosting platform logs
3. Verify audio file format and size
4. Test with a simple audio file first
5. Check GPU availability in your hosting platform

## 🎯 **Next Steps**

After deployment:

1. **Test all endpoints** with sample audio files
2. **Monitor performance** and adjust resources if needed
3. **Set up monitoring** for production use
4. **Consider scaling** if you need higher throughput
5. **Add authentication** if needed for production use

## 💰 **Cost Comparison**

| Platform | Free Tier | Paid Plans | Image Size Limit |
|----------|-----------|------------|------------------|
| **Fly.io** | ✅ 3 VMs, 3GB storage | $1.94/month per VM | None |
| **Heroku** | ❌ No free tier | $7/month Basic | None |
| **Google Cloud Run** | ✅ 2M requests/month | Pay-per-use | None |
| **Railway** | ❌ 4GB limit | $20/month Pro | None |
