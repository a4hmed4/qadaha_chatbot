import requests
import json

def test_chat_api():
    url = "http://localhost:5000/chat"
    headers = {"Content-Type": "application/json"}
    data = {
        "message": "مرحبا، كيف حالك؟",
        "session_id": "test-session-123"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success! Response: {result.get('response', 'No response')}")
        else:
            print(f"Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_chat_api() 