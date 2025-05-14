from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app, origins=["https://blankzz.codeberg.page"])  # Allow frontend origin only

CLIENT_ID = "Ov23liwdZCJXYwgCRNRZ"
CLIENT_SECRET = "ad6a3c0d8842f0a463f86999152484cda646977e"

@app.route('/auth/github/callback')
def github_callback():
    code = request.args.get('code')
    if not code:
        return jsonify({"error": "Missing code"}), 400

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
