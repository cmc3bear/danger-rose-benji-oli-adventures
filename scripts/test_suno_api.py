#!/usr/bin/env python3
"""Test Suno API connection and generate a sample track."""

import requests
import json
import time

SUNO_API_BASE = "https://suno.gcui.ai"

def test_api():
    """Test basic API functionality."""
    print("🧪 Testing Suno API...")
    
    # Test 1: Check API limits
    print("\n1. Checking API limits...")
    try:
        response = requests.get(f"{SUNO_API_BASE}/api/get_limit", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Generate simple test track
    print("\n2. Generating test track...")
    payload = {
        "prompt": "Short 80s synthwave test, 30 seconds",
        "make_instrumental": True,
        "wait_audio": False  # Don't wait, just test endpoint
    }
    
    try:
        response = requests.post(
            f"{SUNO_API_BASE}/api/generate",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response preview: {str(data)[:200]}...")
            
            # Check for IDs to poll status
            if isinstance(data, list) and len(data) > 0:
                track_ids = [item.get('id') for item in data if 'id' in item]
                print(f"   Generated IDs: {track_ids}")
                
                # Test status check
                if track_ids:
                    print(f"\n3. Checking generation status...")
                    time.sleep(2)
                    status_response = requests.get(
                        f"{SUNO_API_BASE}/api/get",
                        params={"ids": track_ids[0]}
                    )
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        print(f"   Status: {status_data[0].get('status', 'unknown')}")
                        if status_data[0].get('audio_url'):
                            print(f"   Audio URL: {status_data[0]['audio_url']}")
        else:
            print(f"   Error response: {response.text[:200]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n✅ API test complete!")

if __name__ == "__main__":
    test_api()