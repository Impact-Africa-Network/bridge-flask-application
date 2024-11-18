from functools import wraps
from flask import request, jsonify, g
import jwt

def token_required(func):
    from app import app
    @wraps(func)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'message': 'Authorization header is missing!'}), 401
            
        try:
            token = auth_header.split(" ")[1]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            g.user = data  # Store decoded token data in Flask's g object
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 403
        except IndexError:
            return jsonify({'message': 'Invalid Authorization header format'}), 401
            
        return func(*args, **kwargs)
    return decorated