from flask import Flask, request, jsonify
from flask_mail import Mail, Message
from flask_cors import CORS
from dotenv import load_dotenv
import os

from utils import verify_recaptcha

load_dotenv()

app = Flask(__name__)
CORS(app)

# Mail configuration
app.config['MAIL_SERVER'] = os.getenv("MAIL_SERVER")
app.config['MAIL_PORT'] = int(os.getenv("MAIL_PORT"))
app.config['MAIL_USE_TLS'] = os.getenv("MAIL_USE_TLS") == "True"
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")

mail = Mail(app)

BUSINESS_EMAIL = os.getenv("BUSINESS_EMAIL")


@app.route("/")
def home():
    return "Contact Mailer API Running ✅"


@app.route("/contact", methods=["POST"])
def contact():
    data = request.get_json()

    fullname = data.get("fullname")
    email = data.get("email")
    company = data.get("company")
    message = data.get("message")

    recaptcha_token = data.get("recaptchaToken")

    if not verify_recaptcha(recaptcha_token):
        return jsonify({"error": "reCAPTCHA verification failed"}), 400

    if not fullname or not email or not company or not message:
        return jsonify({"error": "All fields are required"}), 400

    try:
        msg = Message(
            subject=f"New Contact Message from {fullname}",
            sender=app.config['MAIL_USERNAME'],
            recipients=[BUSINESS_EMAIL],
            body=f"""
You received a new website message:

Name: {fullname}
Email: {email}

Message:
{message}
"""
        )

        mail.send(msg)

        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)