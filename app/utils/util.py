import jwt
from datetime import datetime, timezone, timedelta
from functools import wraps
from flask import request, jsonify


SECRET_KEY = 'nobody knows this key'

def encode_token(user_id):
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(days=0, hours=1),
        'iat': datetime.now(timezone.utc),
        'sub': str(user_id)
    }
    
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split()[1]
            
            if not token:
                return jsonify({'message': 'Missing token'}), 401
            
            try:
                data = jwt.decode(token, SECRET_KEY, algorithms='HS256')
                print(f"Decoded token data: {data}")
                customer_id = data['sub']
            except jwt.ExpiredSignatureError:
                return jsonify({'message': 'Token has expired'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'message': 'Invalid token'}), 401
            
            return f(customer_id, *args, **kwargs)
        
        else:
            return jsonify({'message': 'Must be logged in to access this.'}), 401
        
    return decorated