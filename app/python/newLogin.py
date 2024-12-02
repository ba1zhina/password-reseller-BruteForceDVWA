from flask import Flask, request, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import time
import random
import string

app = Flask(__name__)
app.secret_key = "your_secret_key"


users_db = {
    "admin": generate_password_hash("securepassword123"),
    "user": generate_password_hash("mypassword456")
}

session_tokens = {}
failed_attempts = {}

def generate_token():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))

def rate_limiter(ip):
    if ip not in failed_attempts:
        failed_attempts[ip] = []
    now = time.time()
    failed_attempts[ip] = [t for t in failed_attempts[ip] if now - t < 60]  
    if len(failed_attempts[ip]) >= 5: 
        return False
    failed_attempts[ip].append(now)
    return True

@app.route("/vulnerabilities/brute/", methods=["GET"])
def brute_force_protected():
    ip = request.remote_addr
    if not rate_limiter(ip):
        return jsonify({"error": "Too many attempts. Please wait a minute."}), 429

    username = request.args.get("username")
    password = request.args.get("password")
    user_token = request.args.get("user_token")
    login = request.args.get("Login")

    if user_token != session_tokens.get(session.get("user_id")):
        return jsonify({"error": "Invalid or expired token."}), 403

    if username in users_db and check_password_hash(users_db[username], password):
        return jsonify({"success": "Welcome, {}!".format(username)}), 200

    return jsonify({"error": "Invalid credentials."}), 401

@app.route("/login", methods=["GET"])
def login_page():
    user_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    session["user_id"] = user_id
    token = generate_token()
    session_tokens[user_id] = token

    return jsonify({"user_token": token}), 200

if name == "__main__":
    app.run(host="0.0.0.0", port=5000)