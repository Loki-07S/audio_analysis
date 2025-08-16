#!/usr/bin/env python3
"""
Simple test script for Hugging Face Spaces deployment
"""

import requests
import json
import sys

def test_health_check(base_url):
    """Test the health check endpoint"""
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passed")
            print(f"   Status: {data.get('message', 'Unknown')}")
            print(f"   Platform: {data.get('platform', 'Unknown')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_text_analysis(base_url):
    """Test the text analysis endpoint"""
    try:
        test_text = "Hello world, this is a test message for grammar analysis."
        payload = {"text": test_text}
        response = requests.post(
            f"{base_url}/analyze-text",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Text analysis passed")
            print(f"   Score: {data.get('score', 'Unknown')}")
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
    if len(sys.argv) != 2:
        print("Usage: python test_hf.py <base_url>")
        print("Example: python test_hf.py https://your-space-name.hf.space")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    print(f"🧪 Testing Hugging Face Space: {base_url}")
    print("=" * 50)
    
    # Test health check
    health_ok = test_health_check(base_url)
    print()
    
    # Test text analysis
    text_ok = test_text_analysis(base_url)
    print()
    
    # Summary
    print("=" * 50)
    if health_ok and text_ok:
        print("🎉 All tests passed! Your API is working correctly.")
        print("\n📋 Next steps:")
        print("1. Test with Postman for audio analysis")
        print("2. Upload audio files for speaking/listening analysis")
        print("3. Check the API documentation at the base URL")
    else:
        print("❌ Some tests failed. Check your deployment.")
        if not health_ok:
            print("   - Health check failed - API might not be running")
        if not text_ok:
            print("   - Text analysis failed - Check logs for errors")

if __name__ == "__main__":
    main()
