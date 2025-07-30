import requests
import json

BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

def test_root():
    print("1. Testing root endpoint...")
    response = requests.get(BASE_URL)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

def test_create_user():
    print("2. Testing user creation (will fail without superuser)...")
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123",
        "full_name": "Test User"
    }
    response = requests.post(f"{API_V1}/users/", json=user_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

def test_login():
    print("3. Testing login with admin credentials...")
    login_data = {
        "username": "admin",
        "password": "changeme"
    }
    response = requests.post(
        f"{API_V1}/auth/login/access-token",
        data=login_data
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        token_data = response.json()
        print(f"Response: {token_data}\n")
        return token_data.get("access_token")
    else:
        print(f"Response: {response.text}\n")
        return None

def test_protected_endpoint(token=None):
    print("4. Testing protected endpoint...")
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
        print("   Using authentication token")
    else:
        print("   Without authentication token")
    
    response = requests.get(f"{API_V1}/users/me", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

def test_api_docs():
    print("5. Testing API documentation availability...")
    response = requests.get(f"{BASE_URL}/docs")
    print(f"Status: {response.status_code}")
    print(f"Docs available: {response.status_code == 200}\n")

if __name__ == "__main__":
    print("Smart Yoram API Test Suite\n" + "="*50 + "\n")
    
    test_root()
    test_create_user()
    token = test_login()
    test_protected_endpoint()  # Without token
    if token:
        test_protected_endpoint(token)  # With token
    test_api_docs()
    
    print("="*50)
    print("Test suite completed!")