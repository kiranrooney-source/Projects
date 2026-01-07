from flask import Flask, request, jsonify
import time
import jwt
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

# Mock user credentials
USERS = {
    'admin': 'password123',
    'user1': 'mypass',
    'demo': 'demo123'
}

# Mock databases
DATABASES = [
    'customer_db',
    'inventory_db', 
    'sales_db',
    'analytics_db',
    'logs_db'
]

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            token = token.split(' ')[1]
            jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except:
            return jsonify({'message': 'Token is invalid'}), 401
        
        return f(*args, **kwargs)
    return decorated

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "timestamp": time.time()})

@app.route('/auth', methods=['POST'])
def authenticate():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    auth_type = data.get('auth_type', 'standard')
    
    # Handle Windows authentication
    if auth_type == 'windows':
        # In a real implementation, you would validate Windows credentials
        # For demo purposes, we'll accept any Windows user
        if username and password == 'windows_auth_token':
            token = jwt.encode({
                'username': username,
                'auth_type': 'windows',
                'exp': time.time() + 3600  # 1 hour expiry
            }, app.config['SECRET_KEY'], algorithm='HS256')
            
            return jsonify({
                'token': token,
                'username': username,
                'auth_type': 'windows',
                'message': f'Windows authentication successful for {username}'
            })
    
    # Handle standard authentication
    elif username in USERS and USERS[username] == password:
        token = jwt.encode({
            'username': username,
            'auth_type': 'standard',
            'exp': time.time() + 3600  # 1 hour expiry
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'token': token,
            'username': username,
            'auth_type': 'standard',
            'message': 'Authentication successful'
        })
    
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/databases', methods=['GET'])
@token_required
def get_databases():
    return jsonify({'databases': DATABASES})

@app.route('/query', methods=['POST'])
@token_required
def process_query():
    data = request.get_json()
    requirements = data.get('requirements', '')
    database = data.get('database', '')
    
    # Simulate query processing
    time.sleep(1)
    
    # Mock automated query results based on requirements and database
    result = {
        "query_id": f"Q{int(time.time())}",
        "requirements": requirements,
        "database": database,
        "automated_queries": [
            f"USE {database};",
            f"SELECT * FROM users WHERE requirement LIKE '%{requirements[:20]}%';",
            f"SELECT COUNT(*) FROM logs WHERE description CONTAINS '{requirements[:15]}';",
            f"UPDATE status SET processed = true WHERE task = '{requirements[:10]}';"
        ],
        "execution_time": "1.2s",
        "status": "completed",
        "rows_affected": 42
    }
    
    return jsonify(result)

if __name__ == '__main__':
    print("Server starting...")
    print("Available users: admin/password123, user1/mypass, demo/demo123")
    app.run(host='localhost', port=8000, debug=True)