from flask import Flask, request, jsonify, render_template
from flask_mail import Mail, Message
from flask_cors import CORS
from dotenv import load_dotenv

import os
from datetime import datetime

from utils import verify_recaptcha

load_dotenv()

app = Flask(__name__, template_folder="email_templates")
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


@app.route("/contact-form", methods=["POST"])
def contact():
    data = request.get_json()

    fullname = data.get("fullname")
    email = data.get("email")
    company = data.get("company")
    message = data.get("message")

    recaptcha_token = data.get("recaptchaToken")

    if not fullname or not email or not company or not message:
        return jsonify({"error": "All fields are required"}), 400
    
    if not verify_recaptcha(recaptcha_token):
        return jsonify({"error": "reCAPTCHA verification failed"}), 400

    try:
        html_content = render_template(
            "contact_email.html",
            fullname=fullname,
            email=email,
            company=company,
            message=message,
            year=datetime.now().year
        )

        msg = Message(
            subject=f"New Contact Message from {fullname}",
            sender=app.config['MAIL_USERNAME'],
            recipients=[BUSINESS_EMAIL],
            html=html_content
        )

        mail.send(msg)

        return jsonify({"success": True}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)