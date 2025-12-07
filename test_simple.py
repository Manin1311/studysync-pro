import requests

# Test register endpoint
response = requests.post(
    'http://localhost:5000/api/auth/register',
    json={'email': 'test3@example.com', 'password': 'test123'}
)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

