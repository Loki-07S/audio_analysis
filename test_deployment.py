#!/usr/bin/env python3
"""
Test script for the deployed Audio Analysis API
"""

import requests
import json
import sys
import os

def test_health_check(base_url):
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed!")
            print(f"   Status: {data.get('status')}")
            print(f"   GPU Available: {data.get('gpu_available')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_api_documentation(base_url):
    """Test the API documentation endpoint"""
    print("\n📚 Testing API documentation...")
    try:
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API documentation loaded!")
            print(f"   Version: {data.get('version')}")
            print(f"   Endpoints: {len(data.get('endpoints', {}))}")
            return True
        else:
            print(f"❌ API documentation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API documentation error: {e}")
        return False

def test_speaking_endpoint(base_url, audio_file=None):
    """Test the speaking analysis endpoint"""
    print("\n🎤 Testing speaking analysis endpoint...")
    
    if not audio_file or not os.path.exists(audio_file):
        print("⚠️  No audio file provided or file doesn't exist. Skipping speaking test.")
        return True
    
    try:
        with open(audio_file, 'rb') as f:
            files = {'audio': f}
            response = requests.post(f"{base_url}/speaking", files=files, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Speaking analysis successful!")
            print(f"   Overall Score: {data.get('score', 'N/A')}")
            print(f"   Fluency Score: {data.get('report', {}).get('fluency_analysis', {}).get('score', 'N/A')}")
            print(f"   Grammar Score: {data.get('report', {}).get('grammar_analysis', {}).get('score', 'N/A')}")
            return True
        else:
            print(f"❌ Speaking analysis failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Speaking analysis error: {e}")
        return False

def test_listening_endpoint(base_url, audio_file=None):
    """Test the listening analysis endpoint"""
    print("\n👂 Testing listening analysis endpoint...")
    
    if not audio_file or not os.path.exists(audio_file):
        print("⚠️  No audio file provided or file doesn't exist. Skipping listening test.")
        return True
    
    test_text = "This is a test text for listening analysis. The audio should match this text for good similarity scores."
    
    try:
        with open(audio_file, 'rb') as f:
            files = {'audio': f}
            data = {'text': test_text}
            response = requests.post(f"{base_url}/listening", files=files, data=data, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Listening analysis successful!")
            print(f"   Overall Score: {data.get('score', 'N/A')}")
            print(f"   Similarity Score: {data.get('report', {}).get('similarity_analysis', {}).get('score', 'N/A')}")
            return True
        else:
            print(f"❌ Listening analysis failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Listening analysis error: {e}")
        return False

def test_text_analysis_endpoint(base_url):
    """Test the text-only analysis endpoint"""
    print("\n📝 Testing text analysis endpoint...")
    
    test_text = "This is a test text for grammar and professionalism analysis. It should demonstrate good writing skills."
    
    try:
        data = {'text': test_text}
        response = requests.post(f"{base_url}/analyze-text", json=data, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Text analysis successful!")
            print(f"   Overall Score: {data.get('score', 'N/A')}")
            print(f"   Grammar Score: {data.get('report', {}).get('grammar_analysis', {}).get('score', 'N/A')}")
            return True
        else:
            print(f"❌ Text analysis failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Text analysis error: {e}")
        return False

def main():
    """Main test function"""
    if len(sys.argv) < 2:
        print("Usage: python test_deployment.py <base_url> [audio_file]")
        print("Example: python test_deployment.py https://your-app.railway.app test.mp3")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    audio_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"🚀 Testing Audio Analysis API at: {base_url}")
    print("=" * 50)
    
    tests = [
        test_health_check,
        test_api_documentation,
        test_speaking_endpoint,
        test_listening_endpoint,
        test_text_analysis_endpoint
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test(base_url, audio_file):
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the deployment and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
