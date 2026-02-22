import os
import requests

def verify_recaptcha(token):
    secret = os.getenv("RECAPTCHA_SECRET")

    response = requests.post(
        "https://www.google.com/recaptcha/api/siteverify",
        data={
            "secret": secret,
            "response": token
        }
    )

    result = response.json()
    return result.get("success", False)