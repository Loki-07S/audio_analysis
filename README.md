# Audio Analysis API

A comprehensive audio analysis system that evaluates speaking skills, listening comprehension, and text quality using advanced AI models.

## 🚀 **Deployed on Hugging Face Spaces**

This API is deployed on Hugging Face Spaces with GPU support for optimal performance.

## 📋 **API Endpoints**

### **1. Health Check**
```http
GET /
```
Returns API status and GPU availability.

### **2. Speaking Analysis**
```http
POST /speaking
```
Analyzes audio for fluency, grammar, and professionalism.

**Request**: Upload audio file using `multipart/form-data` with field name `audio`

**Supported formats**: WAV, MP3, M4A, FLAC, OGG

### **3. Listening Analysis**
```http
POST /listening
```
Compares audio with provided text for similarity assessment.

**Request**: 
- Upload audio file using `multipart/form-data` with field name `audio`
- Include text field with reference text

### **4. Text Analysis**
```http
POST /analyze-text
```
Analyzes text for grammar and professionalism.

**Request**: JSON with `text` field

## 🧪 **Testing with Postman**

### **Health Check**
- **Method**: GET
- **URL**: `https://your-space-name.hf.space/`
- **Headers**: None

### **Speaking Analysis**
- **Method**: POST
- **URL**: `https://your-space-name.hf.space/speaking`
- **Body**: form-data
  - Key: `audio` (Type: File)
  - Upload your audio file

### **Listening Analysis**
- **Method**: POST
- **URL**: `https://your-space-name.hf.space/listening`
- **Body**: form-data
  - Key: `audio` (Type: File) - Upload audio file
  - Key: `text` (Type: Text) - Enter reference text

### **Text Analysis**
- **Method**: POST
- **URL**: `https://your-space-name.hf.space/analyze-text`
- **Headers**: `Content-Type: application/json`
- **Body**: 
```json
{
  "text": "Your text to analyze for grammar and professionalism."
}
```

## 📊 **Response Format**

### **Speaking/Listening Analysis Response**
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

### **Text Analysis Response**
```json
{
  "score": 88.0,
  "report": {
    "grammar_analysis": {
      "score": 90,
      "analysis": ["Excellent grammar"],
      "errors": [],
      "error_count": 0
    },
    "professionalism_analysis": {
      "score": 85,
      "analysis": ["Professional language use"]
    }
  }
}
```

## 🔧 **Features**

- **GPU Support**: Automatic GPU acceleration when available
- **Multiple Audio Formats**: WAV, MP3, M4A, FLAC, OGG
- **Comprehensive Analysis**: Fluency, grammar, professionalism, similarity
- **Real-time Processing**: Fast analysis with advanced AI models
- **Error Handling**: Robust error handling and validation

## 🛠️ **Technical Stack**

- **Backend**: Flask (Python)
- **Audio Processing**: OpenAI Whisper, PyDub
- **Text Analysis**: LanguageTool, TextBlob
- **ML Framework**: PyTorch
- **Deployment**: Hugging Face Spaces

## 📈 **Performance**

- **Processing Time**: 10-30 seconds per audio file
- **File Size Limit**: 16MB per audio file
- **Concurrent Requests**: Optimized for single-user processing
- **GPU Acceleration**: Automatic when available

## 🎯 **Use Cases**

- **Language Learning**: Assess speaking and listening skills
- **Interview Preparation**: Practice and improve communication
- **Educational Assessment**: Evaluate student performance
- **Professional Development**: Enhance communication skills

## 🔒 **Security**

- **File Validation**: Strict file type checking
- **Temporary Storage**: Files are automatically cleaned up
- **No Data Retention**: Audio files are not stored permanently
- **Input Validation**: Comprehensive request validation

## 📞 **Support**

For issues or questions:
1. Check the health endpoint for API status
2. Verify audio file format and size
3. Ensure proper request format
4. Check Hugging Face Spaces logs

## 🚀 **Deployment**

This API is deployed on Hugging Face Spaces with:
- **GPU Support**: Automatic GPU acceleration
- **Auto-scaling**: Handles traffic spikes
- **Global CDN**: Fast response times worldwide
- **SSL Security**: HTTPS encryption
