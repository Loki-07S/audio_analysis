# Audio Analysis API - Hugging Face Spaces

This is a Flask-based API for comprehensive audio analysis, deployed on Hugging Face Spaces with GPU support.

## 🚀 **Quick Start**

1. **Fork this repository** to your Hugging Face account
2. **Create a new Space** on Hugging Face
3. **Select "Docker"** as the SDK
4. **Connect your forked repository**
5. **Enable GPU** in the Space settings
6. **Deploy!**

## 📋 **API Endpoints**

### **Health Check**
```http
GET /
```
Returns API status and GPU availability.

### **Speaking Analysis**
```http
POST /speaking
```
Analyzes audio for fluency, grammar, and professionalism.

### **Listening Analysis**
```http
POST /listening
```
Compares audio with provided text for similarity assessment.

### **Text Analysis**
```http
POST /analyze-text
```
Analyzes text for grammar and professionalism.

## 🧪 **Testing**

### **With Postman**
1. **Health Check**: `GET https://your-space-name.hf.space/`
2. **Speaking Analysis**: `POST https://your-space-name.hf.space/speaking` (form-data with audio file)
3. **Listening Analysis**: `POST https://your-space-name.hf.space/listening` (form-data with audio file and text)
4. **Text Analysis**: `POST https://your-space-name.hf.space/analyze-text` (JSON with text field)

### **With curl**
```bash
# Health check
curl https://your-space-name.hf.space/

# Speaking analysis
curl -X POST -F "audio=@your_audio.mp3" https://your-space-name.hf.space/speaking

# Text analysis
curl -X POST -H "Content-Type: application/json" -d '{"text":"Hello world"}' https://your-space-name.hf.space/analyze-text
```

## 🔧 **Configuration**

### **Space Settings**
- **SDK**: Docker
- **Hardware**: GPU (recommended)
- **Python Version**: 3.9+
- **Port**: 7860

### **Environment Variables**
- `PORT`: 7860 (default)
- `MAX_CONTENT_LENGTH`: 16777216 (16MB)

## 📊 **Features**

- **GPU Acceleration**: Automatic when available
- **Multiple Audio Formats**: WAV, MP3, M4A, FLAC, OGG
- **Comprehensive Analysis**: Fluency, grammar, professionalism, similarity
- **Real-time Processing**: Fast analysis with AI models
- **Error Handling**: Robust validation and error responses

## 🛠️ **Technical Details**

- **Backend**: Flask
- **Audio Processing**: OpenAI Whisper, PyDub
- **Text Analysis**: LanguageTool, TextBlob
- **ML Framework**: PyTorch
- **Deployment**: Hugging Face Spaces

## 📈 **Performance**

- **Processing Time**: 10-30 seconds per audio file
- **File Size Limit**: 16MB per audio file
- **GPU Support**: Automatic acceleration
- **Concurrent Requests**: Optimized for single-user processing

## 🎯 **Use Cases**

- Language learning assessment
- Interview preparation
- Educational evaluation
- Professional development

## 🔒 **Security**

- File type validation
- Temporary file storage
- No data retention
- Input validation

## 📞 **Support**

For issues:
1. Check the health endpoint
2. Verify file format and size
3. Check Space logs
4. Ensure proper request format
