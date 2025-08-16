from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import tempfile
from audio_analysis import analyze_audio, analyze_audio_with_text

app = Flask(__name__)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a', 'flac', 'ogg'}

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        import torch
        gpu_available = torch.cuda.is_available()
    except ImportError:
        gpu_available = False
    
    return jsonify({
        "status": "healthy",
        "message": "Audio Analysis API is running",
        "gpu_available": gpu_available,
        "platform": "Hugging Face Spaces"
    })

@app.route('/speaking', methods=['POST'])
def speaking_analysis():
    """
    Speaking analysis endpoint - audio only
    
    Expected request:
    - audio file in multipart/form-data
    
    Returns:
    - JSON with fluency, grammar, and professionalism analysis
    """
    try:
        # Check if audio file is present
        if 'audio' not in request.files:
            return jsonify({
                "error": "No audio file provided",
                "message": "Please upload an audio file using the 'audio' field"
            }), 400
        
        audio_file = request.files['audio']
        
        # Check if file is selected
        if audio_file.filename == '':
            return jsonify({
                "error": "No file selected",
                "message": "Please select an audio file to upload"
            }), 400
        
        # Check file extension
        if not allowed_file(audio_file.filename):
            return jsonify({
                "error": "Invalid file type",
                "message": f"Allowed file types: {', '.join(ALLOWED_EXTENSIONS)}"
            }), 400
        
        # Save the uploaded file temporarily
        filename = secure_filename(audio_file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        audio_file.save(temp_path)
        
        try:
            # Analyze audio only (speaking assessment)
            result = analyze_audio(temp_path)
            return jsonify(result)
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        return jsonify({
            "error": "Analysis failed",
            "message": str(e)
        }), 500

@app.route('/listening', methods=['POST'])
def listening_analysis():
    """
    Listening analysis endpoint - audio + custom text for similarity
    
    Expected request:
    - audio file in multipart/form-data
    - text field for custom transcription (required)
    
    Returns:
    - JSON with similarity, fluency, and grammar analysis
    """
    try:
        # Check if audio file is present
        if 'audio' not in request.files:
            return jsonify({
                "error": "No audio file provided",
                "message": "Please upload an audio file using the 'audio' field"
            }), 400
        
        audio_file = request.files['audio']
        
        # Check if file is selected
        if audio_file.filename == '':
            return jsonify({
                "error": "No file selected",
                "message": "Please select an audio file to upload"
            }), 400
        
        # Check file extension
        if not allowed_file(audio_file.filename):
            return jsonify({
                "error": "Invalid file type",
                "message": f"Allowed file types: {', '.join(ALLOWED_EXTENSIONS)}"
            }), 400
        
        # Check if custom text is provided (required for listening)
        custom_text = request.form.get('text', None)
        if not custom_text:
            return jsonify({
                "error": "No text provided",
                "message": "Please provide text field for listening analysis"
            }), 400
        
        # Save the uploaded file temporarily
        filename = secure_filename(audio_file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        audio_file.save(temp_path)
        
        try:
            # Analyze audio with custom text (listening assessment)
            result = analyze_audio_with_text(temp_path, custom_text)
            return jsonify(result)
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        return jsonify({
            "error": "Analysis failed",
            "message": str(e)
        }), 500

@app.route('/analyze-text', methods=['POST'])
def analyze_text_only():
    """
    Analyze text only (without audio) for grammar and professionalism
    
    Expected request:
    - JSON with 'text' field
    
    Returns:
    - JSON with grammar and professionalism analysis only
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                "error": "No text provided",
                "message": "Please provide text in JSON format with 'text' field"
            }), 400
        
        text = data['text']
        
        if not text.strip():
            return jsonify({
                "error": "Empty text",
                "message": "Please provide non-empty text"
            }), 400
        
        # Import the analysis functions
        from audio_analysis import analyze_grammar_advanced, analyze_professionalism, calculate_overall_score
        
        # Analyze grammar and professionalism
        grammar_analysis = analyze_grammar_advanced(text)
        professionalism_analysis = analyze_professionalism(text)
        
        # Calculate overall score (fluency score will be 0 since no audio)
        overall_score = calculate_overall_score(0, grammar_analysis["score"], professionalism_analysis["score"])
        
        result = {
            "score": overall_score,
            "report": {
                "grammar_analysis": {
                    "score": grammar_analysis["score"],
                    "analysis": grammar_analysis["analysis"],
                    "errors": grammar_analysis["errors"],
                    "error_count": grammar_analysis["error_count"]
                },
                "professionalism_analysis": {
                    "score": professionalism_analysis["score"],
                    "analysis": professionalism_analysis["analysis"]
                }
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "error": "Analysis failed",
            "message": str(e)
        }), 500

@app.route('/', methods=['GET'])
def index():
    """API documentation endpoint"""
    return jsonify({
        "message": "Audio Analysis API",
        "version": "1.0.0",
        "platform": "Hugging Face Spaces",
        "endpoints": {
            "GET /": "API documentation (this endpoint)",
            "GET /health": "Health check",
            "POST /speaking": "Speaking analysis - audio only (fluency, grammar, professionalism)",
            "POST /listening": "Listening analysis - audio + text (similarity, fluency, grammar)",
            "POST /analyze-text": "Text analysis only (grammar and professionalism)"
        },
        "usage": {
            "/speaking": "Upload audio file using multipart/form-data with 'audio' field for speaking assessment.",
            "/listening": "Upload audio file using multipart/form-data with 'audio' field and 'text' field for listening assessment.",
            "/analyze-text": "Send JSON with 'text' field for grammar and professionalism analysis only."
        },
        "supported_audio_formats": list(ALLOWED_EXTENSIONS)
    })

if __name__ == '__main__':
    # Use port 7860 for Hugging Face Spaces
    port = int(os.environ.get('PORT', 7860))
    app.run(debug=False, host='0.0.0.0', port=port)
