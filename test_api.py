import requests
import json
import os

# API base URL
BASE_URL = "http://localhost:5000"

def test_health():
    """Test health check endpoint"""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_index():
    """Test API documentation endpoint"""
    print("Testing API documentation...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_speaking_analysis():
    """Test speaking analysis endpoint (audio only)"""
    print("Testing speaking analysis...")
    
    # Check if test audio file exists
    test_audio_path = "test_audio.wav"  # You'll need to provide a test audio file
    if not os.path.exists(test_audio_path):
        print(f"Test audio file not found: {test_audio_path}")
        print("Please provide a test audio file named 'test_audio.wav'")
        return
    
    with open(test_audio_path, 'rb') as audio_file:
        files = {'audio': audio_file}
        response = requests.post(f"{BASE_URL}/speaking", files=files)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Overall Score: {result.get('score', 'N/A')}")
        print(f"Report Keys: {list(result.get('report', {}).keys())}")
        print("Full Response:")
        print(json.dumps(result, indent=2))
    else:
        print(f"Error: {response.json()}")
    print("-" * 50)

def test_listening_analysis():
    """Test listening analysis endpoint (audio + text)"""
    print("Testing listening analysis...")
    
    # Check if test audio file exists
    test_audio_path = "test_audio.wav"  # You'll need to provide a test audio file
    if not os.path.exists(test_audio_path):
        print(f"Test audio file not found: {test_audio_path}")
        print("Please provide a test audio file named 'test_audio.wav'")
        return
    
    # Sample reference text for listening test
    reference_text = "This is a sample reference text for listening analysis. The user should speak this text accurately."
    
    with open(test_audio_path, 'rb') as audio_file:
        files = {'audio': audio_file}
        data = {'text': reference_text}
        response = requests.post(f"{BASE_URL}/listening", files=files, data=data)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Overall Score: {result.get('score', 'N/A')}")
        print(f"Report Keys: {list(result.get('report', {}).keys())}")
        print("Full Response:")
        print(json.dumps(result, indent=2))
    else:
        print(f"Error: {response.json()}")
    print("-" * 50)

def test_text_analysis():
    """Test text-only analysis endpoint"""
    print("Testing text analysis...")
    
    sample_text = "This is a sample text for grammar and professionalism analysis. It contains some basic sentences."
    
    data = {'text': sample_text}
    response = requests.post(f"{BASE_URL}/analyze-text", json=data)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Overall Score: {result.get('score', 'N/A')}")
        print(f"Report Keys: {list(result.get('report', {}).keys())}")
        print("Full Response:")
        print(json.dumps(result, indent=2))
    else:
        print(f"Error: {response.json()}")
    print("-" * 50)

if __name__ == "__main__":
    print("Audio Analysis API Testing")
    print("=" * 50)
    
    # Run all tests
    test_health()
    test_index()
    test_speaking_analysis()
    test_listening_analysis()
    test_text_analysis()
    
    print("Testing completed!")
