from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from functools import wraps

app = Flask(__name__)

# Configure CORS properly
CORS(
    app,
    resources={
        r"/auth/github/callback": {
            "origins": ["https://blankzz.codeberg.page"],
            "methods": ["GET"],
            "allow_headers": ["Content-Type"]
        }
    },
    supports_credentials=True
)

# Environment variables for security
CLIENT_ID = os.environ.get("GITHUB_CLIENT_ID")
CLIENT_SECRET = os.environ.get("GITHUB_CLIENT_SECRET")

def add_cors_headers(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = f(*args, **kwargs)
        response.headers.add('Access-Control-Allow-Origin', 'https://blankzz.codeberg.page')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
    return decorated_function

@app.route("/auth/github/callback", methods=['GET', 'OPTIONS'])
@add_cors_headers
def github_callback():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    code = request.args.get("code")
    if not code:
        return jsonify({"error": "Missing authorization code"}), 400

    try:
        # Exchange code for access token
        token_response = requests.post(
            "https://github.com/login/oauth/access_token",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            json={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "code": code
            },
            timeout=10
        )
        token_response.raise_for_status()
        token_data = token_response.json()

        access_token = token_data.get("access_token")
        if not access_token:
            return jsonify({"error": "Failed to get access token"}), 400

        # Get user info
        user_response = requests.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"token {access_token}",
                "Accept": "application/json"
            },
            timeout=10
        )
        user_response.raise_for_status()
        user_data = user_response.json()

        # Get primary email
        email_response = requests.get(
            "https://api.github.com/user/emails",
            headers={
                "Authorization": f"token {access_token}",
                "Accept": "application/json"
            },
            timeout=10
        )
        email_response.raise_for_status()
        email_data = email_response.json()
        primary_email = next((email["email"] for email in email_data if email.get("primary")), None)

        return jsonify({
            "login": user_data.get("login"),
            "email": primary_email
        })

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"GitHub API error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
