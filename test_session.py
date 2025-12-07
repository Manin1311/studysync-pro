import requests

# Test session persistence
session = requests.Session()

print("1. Testing login...")
response = session.post(
    'http://localhost:5000/api/auth/login',
    json={'email': 'test@example.com', 'password': 'test123'}
)
print(f"Login status: {response.status_code}")
print(f"Login response: {response.json()}")
print(f"Cookies after login: {session.cookies}")

print("\n2. Testing get current user...")
response = session.get('http://localhost:5000/api/auth/me')
print(f"Get user status: {response.status_code}")
print(f"Get user response: {response.text}")
print(f"Cookies: {session.cookies}")

print("\n3. Testing create note...")
response = session.post(
    'http://localhost:5000/api/notes',
    json={'course_id': 1, 'title': 'Test', 'content': 'Test content'}
)
print(f"Create note status: {response.status_code}")
print(f"Create note response: {response.text}")

