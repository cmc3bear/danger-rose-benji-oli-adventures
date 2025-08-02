#!/usr/bin/env python3
"""Test OpenAI API connection."""

import requests
import json
import os

# API Configuration
# IMPORTANT: Set your OpenAI API key as an environment variable:
# export OPENAI_API_KEY='your-api-key-here'
API_KEY = os.getenv('OPENAI_API_KEY')
if not API_KEY:
    raise ValueError("Please set OPENAI_API_KEY environment variable")

def test_api():
    """Test API with a simple request."""
    print("Testing OpenAI API...")
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Test with models endpoint
    try:
        response = requests.get(
            "https://api.openai.com/v1/models",
            headers=headers,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            models = response.json()
            print("[OK] API connection successful!")
            print(f"Available models: {len(models.get('data', []))}")
            
            # Check for DALL-E
            dalle_models = [m for m in models.get('data', []) if 'dall-e' in m.get('id', '').lower()]
            if dalle_models:
                print("\nDALL-E models found:")
                for model in dalle_models:
                    print(f"  - {model['id']}")
            else:
                print("\n[WARNING] No DALL-E models found")
        else:
            print(f"[ERROR] {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    test_api()