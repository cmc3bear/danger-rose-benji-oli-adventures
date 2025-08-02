"""Test OpenAI API connection."""

import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.vault_utils import get_api_key

try:
    from openai import OpenAI
except ImportError:
    print("OpenAI library not installed. Installing...")
    os.system("pip install openai")
    from openai import OpenAI

def test_connection():
    """Test OpenAI API connection."""
    print("Testing OpenAI API connection...")
    
    try:
        # Get API key
        api_key = get_api_key("OPENAI")
        print(f"[OK] API key loaded (length: {len(api_key)})")
        
        # Initialize client
        client = OpenAI(api_key=api_key)
        print("[OK] OpenAI client initialized")
        
        # Test with a simple completion
        print("Testing API with simple completion...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'API working'"}],
            max_tokens=10
        )
        print(f"[OK] API Response: {response.choices[0].message.content}")
        
        # Test image generation model availability
        print("\nTesting DALL-E 3 availability...")
        try:
            test_response = client.images.generate(
                model="dall-e-3",
                prompt="A simple red circle on white background",
                size="1024x1024",
                quality="standard",
                n=1,
            )
            print("[OK] DALL-E 3 is available and working")
            print(f"Test image URL: {test_response.data[0].url[:50]}...")
        except Exception as e:
            print(f"[ERROR] DALL-E 3 test failed: {type(e).__name__}: {e}")
            
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_connection()