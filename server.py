from flask import Flask, request, redirect, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app, origins=["https://blankzz.codeberg.page"])

# Replace these with your GitHub app credentials
CLIENT_ID = os.environ.get("GITHUB_CLIENT_ID", "Ov23liwdZCJXYwgCRNRZ")
CLIENT_SECRET = os.environ.get("GITHUB_CLIENT_SECRET", "ad6a3c0d8842f0a463f86999152484cda646977e")

@app.route("/")
def home():
    return "OAuth server is running."

@app.route("/auth/github/callback")
def github_callback():
    code = request.args.get("code")
    if not code:
        return jsonify({"error": "Missing authorization code"}), 400

    # Exchange code for access token
    token_response = requests.post(
        "https://github.com/login/oauth/access_token",
        headers={"Accept": "application/json"},
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code
        }
    )

    token_data = token_response.json()
    access_token = token_data.get("access_token")
    if not access_token:
        return jsonify({"error": "Failed to get access token"}), 400

    # Get user info
    user_response = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"token {access_token}"}
    )
    user_data = user_response.json()

    # Optional: get email if needed
    email_response = requests.get(
        "https://api.github.com/user/emails",
        headers={"Authorization": f"token {access_token}"}
    )
    email_data = email_response.json()
    primary_email = next((email["email"] for email in email_data if email["primary"]), None)

    return jsonify({
        "login": user_data.get("login"),
        "email": primary_email
    })

if __name__ == "__main__":
    app.run(debug=True)
