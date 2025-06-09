"""Script to test API endpoints with detailed error reporting."""
import requests
import json
import sys
import traceback

def test_endpoint(url, method="GET", data=None, headers=None):
    """Test an API endpoint and print detailed information."""
    print(f"\n🔍 Testing {method} {url}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        else:
            print(f"❌ Unsupported method: {method}")
            return
        
        # Print response details
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        
        # Try to parse and print JSON response
        try:
            json_response = response.json()
            print(f"📄 Response Body (JSON):")
            print(json.dumps(json_response, indent=2))
        except ValueError:
            # Not JSON, print as text
            print(f"📄 Response Body (Text):")
            print(response.text[:500] + ("..." if len(response.text) > 500 else ""))
        
        return response
    
    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()
        return None

def main():
    """Test main API endpoints."""
    base_url = "http://127.0.0.1:8000"
    
    # Test spending endpoint
    print("\n🧪 Testing Spending API")
    test_endpoint(f"{base_url}/api/v1/spending/")
    
    # Test recommendations endpoint
    print("\n🧪 Testing Recommendations API")
    test_endpoint(f"{base_url}/api/v1/recommendations/")

if __name__ == "__main__":
    main()
