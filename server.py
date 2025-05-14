from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Replace with your GitHub App credentials
CLIENT_ID = "Ov23liwdZCJXYwgCRNRZ"
CLIENT_SECRET = "your_client_secret_here"

@app.route('/auth/github/callback')
def github_callback():
    code = request.args.get('code')
    if not code:
        return jsonify({"error": "Missing code"}), 400

    # Step 1: Exchange code for access token
    token_res = requests.post(
        "https://github.com/login/oauth/access_token",
        headers={"Accept": "application/json"},
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code
        }
    )
    token_json = token_res.json()
    access_token = token_json.get("access_token")
    if not access_token:
        return jsonify({"error": "Failed to get access token"}), 400

    # Step 2: Get user info
    user_res = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    email_res = requests.get(
        "https://api.github.com/user/emails",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    user_data = user_res.json()
    emails = email_res.json()
    primary_email = next((e["email"] for e in emails if e.get("primary")), None)

    return jsonify({
        "login": user_data.get("login"),
        "email": primary_email or user_data.get("email")
    })

@app.route('/')
def home():
    return "GitHub Auth Backend is running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0')
