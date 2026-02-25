from flask import Blueprint, request, jsonify, session
from datetime import datetime
import hashlib

auth_bp = Blueprint('auth', __name__)

# Demo users (production: use database)
USERS = {
    "admin": hashlib.sha256("admin123".encode()).hexdigest(),
    "user": hashlib.sha256("user123".encode()).hexdigest(),
    "nivetha": hashlib.sha256("ai2026".encode()).hexdigest()  # Yours! 😊
}

@auth_bp.route('/login', methods=['POST'])
def login():
    """Simple login with session"""
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    # Verify password
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    if username in USERS and USERS[username] == password_hash:
        # Set session (React uses cookies)
        session['username'] = username
        session['logged_in'] = True
        session['login_time'] = datetime.now().isoformat()
        
        return jsonify({
            "success": True,
            "message": f"Welcome {username}!",
            "user": {
                "username": username,
                "role": "admin" if username == "admin" else "user"
            }
        })
    
    return jsonify({
        "success": False, 
        "error": "Invalid username or password"
    }), 401

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Clear session"""
    session.clear()
    return jsonify({
        "success": True, 
        "message": "Logged out successfully"
    })

@auth_bp.route('/me', methods=['GET'])
def get_me():
    """Current user info"""
    if session.get('logged_in'):
        return jsonify({
            "authenticated": True,
            "username": session['username'],
            "login_time": session.get('login_time')
        })
    return jsonify({"authenticated": False}), 401

@auth_bp.route('/check', methods=['GET'])
def check_status():
    """Quick auth check for frontend"""
    return jsonify({
        "isLoggedIn": bool(session.get('logged_in')),
        "username": session.get('username', 'Guest')
    })

@auth_bp.route('/demo-users', methods=['GET'])
def get_demo_users():
    """Demo login credentials"""
    return jsonify({
        "demo_accounts": [
            {"username": "admin", "password": "admin123", "role": "Admin"},
            {"username": "user", "password": "user123", "role": "User"},
            {"username": "nivetha", "password": "ai2026", "role": "User"}
        ]
    })
