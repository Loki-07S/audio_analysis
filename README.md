# Audio Analysis Model

A comprehensive audio analysis system that evaluates speaking skills including fluency, grammar, and professionalism. The model provides detailed JSON reports with scoring for each component.

## Features

- **Audio-only Fluency Analysis**: Analyzes speech patterns, rhythm, and flow using audio characteristics
- **Grammar Analysis**: Checks grammar, spelling, and sentence structure using transcribed text
- **Professionalism Analysis**: Evaluates language formality, vocabulary diversity, and communication style
- **Similarity Analysis**: Compares transcribed audio with custom reference text (for listening assessment)
- **RESTful API**: Flask-based API with separate endpoints for different analysis types
- **JSON Output**: Structured JSON responses with detailed scoring and analysis

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the Flask application:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### 1. Speaking Analysis (`POST /speaking`)
Analyzes audio for speaking skills (fluency, grammar, professionalism).

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: 
  - `audio`: Audio file (WAV, MP3, M4A, FLAC, OGG)

**Response:**
```json
{
  "score": 85.6,
  "report": {
    "fluency_analysis": {
      "score": 83,
      "analysis": ["Good speech activity", "Excellent speech rate"]
    },
    "grammar_analysis": {
      "score": 88,
      "analysis": ["Good grammar with minor errors"],
      "errors": ["Possible spelling mistake found"],
      "error_count": 1
    },
    "professionalism_analysis": {
      "score": 85,
      "analysis": ["Excellent professional language"]
    }
  }
}
```

### 2. Listening Analysis (`POST /listening`)
Analyzes audio against custom reference text for listening assessment (similarity, fluency, grammar).

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body:
  - `audio`: Audio file (WAV, MP3, M4A, FLAC, OGG)
  - `text`: Reference text to compare against (required)

**Response:**
```json
{
  "score": 78.4,
  "report": {
    "similarity_analysis": {
      "score": 90,
      "errors": {
        "substitutions": [{"from": "reference", "to": "refference"}],
        "insertions": ["um"],
        "deletions": ["the"]
      },
      "summary": ["2 substitutions detected", "Substitution penalty: -10"]
    },
    "fluency_analysis": {
      "score": 75,
      "analysis": ["Good speech activity", "Moderate speech rate"]
    },
    "grammar_analysis": {
      "score": 70,
      "analysis": ["Some grammar errors detected"],
      "errors": ["Possible spelling mistake found"],
      "error_count": 1
    }
  }
}
```

### 3. Text Analysis (`POST /analyze-text`)
Analyzes text only for grammar and professionalism.

**Request:**
- Method: `POST`
- Content-Type: `application/json`
- Body:
```json
{
  "text": "Your text to analyze here."
}
```

**Response:**
```json
{
  "score": 82.0,
  "report": {
    "grammar_analysis": {
      "score": 85,
      "analysis": ["Good grammar with minor errors"],
      "errors": ["Possible spelling mistake found"],
      "error_count": 1
    },
    "professionalism_analysis": {
      "score": 79,
      "analysis": ["Good professional language"]
    }
  }
}
```

### 4. Health Check (`GET /health`)
Returns API health status.

### 5. API Documentation (`GET /`)
Returns API documentation and usage information.

## Usage Examples

### Using curl

**Speaking Analysis:**
```bash
curl -X POST -F "audio=@your_audio.wav" http://localhost:5000/speaking
```

**Listening Analysis:**
```bash
curl -X POST -F "audio=@your_audio.wav" -F "text=Your reference text here" http://localhost:5000/listening
```

**Text Analysis:**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"text":"Your text to analyze"}' \
  http://localhost:5000/analyze-text
```

### Using Python

```python
import requests

# Speaking analysis
with open('audio.wav', 'rb') as f:
    response = requests.post('http://localhost:5000/speaking', 
                           files={'audio': f})
    result = response.json()
    print(f"Speaking Score: {result['score']}")

# Listening analysis
with open('audio.wav', 'rb') as f:
    response = requests.post('http://localhost:5000/listening',
                           files={'audio': f},
                           data={'text': 'Reference text to compare'})
    result = response.json()
    print(f"Listening Score: {result['score']}")

# Text analysis
response = requests.post('http://localhost:5000/analyze-text',
                        json={'text': 'Text to analyze'})
result = response.json()
print(f"Text Score: {result['score']}")
```

## Supported Audio Formats

- WAV
- MP3
- M4A
- FLAC
- OGG

## Analysis Components

### Speaking Analysis
- **Fluency Analysis**: Audio-based analysis of speech patterns, rhythm, and flow
- **Grammar Analysis**: Text-based grammar and spelling checking
- **Professionalism Analysis**: Language formality and communication style evaluation

### Listening Analysis
- **Similarity Analysis**: Compares transcribed audio with reference text
- **Fluency Analysis**: Audio-based speech pattern analysis
- **Grammar Analysis**: Text-based grammar checking

### Text Analysis
- **Grammar Analysis**: Grammar and spelling checking
- **Professionalism Analysis**: Language formality evaluation

## Scoring System

### Speaking Analysis Weighting
- Overall Score: 50% fluency + 30% grammar + 20% professionalism

### Listening Analysis Weighting
- Overall Score: 60% similarity + 20% fluency + 20% grammar

### Score Ranges
- **Excellent**: 85-100 points
- **Good**: 70-84 points
- **Moderate**: 55-69 points
- **Below Average**: 40-54 points
- **Poor**: 20-39 points

## Similarity Analysis Details

The similarity analysis uses Word Error Rate (WER) with strict penalties:
- **Substitution Penalty**: -5 points per substitution
- **Deletion Penalty**: -3 points per deletion
- **Insertion Penalty**: -2 points per insertion
- **Base Score**: 100 - (sum of all penalties)

## Performance

- **Audio Processing**: Real-time analysis for files up to 16MB
- **Transcription**: Uses OpenAI Whisper for accurate speech-to-text
- **Grammar Checking**: LanguageTool integration for comprehensive grammar analysis
- **API Response**: Typically responds within 5-10 seconds

## Testing

Run the test script to verify API functionality:

```bash
python test_api.py
```

Make sure to provide a test audio file named `test_audio.wav` in the project directory.

## API Testing with Postman

1. **Speaking Analysis:**
   - Method: `POST`
   - URL: `http://localhost:5000/speaking`
   - Body: `form-data`
   - Key: `audio` (Type: File)
   - Value: Select your audio file

2. **Listening Analysis:**
   - Method: `POST`
   - URL: `http://localhost:5000/listening`
   - Body: `form-data`
   - Key: `audio` (Type: File)
   - Key: `text` (Type: Text)
   - Value: Your reference text

3. **Text Analysis:**
   - Method: `POST`
   - URL: `http://localhost:5000/analyze-text`
   - Body: `raw` (JSON)
   - Content-Type: `application/json`
   - Body: `{"text": "Your text here"}`

## Future Enhancements

- Multi-language support
- Real-time streaming analysis
- Advanced pronunciation scoring
- Emotion detection
- Speaker identification
- Custom scoring weights
- Batch processing capabilities
