import os
import requests

VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"

def verify_recaptcha(recaptcha_response):
    secret_key = os.getenv("RECAPTCHA_SECRET_KEY")

    if not secret_key or not recaptcha_response:
        return False

    data = {
        "secret": secret_key,
        "response": recaptcha_response
    }

    try:
        response = requests.post(VERIFY_URL, data=data, timeout=5)
        result = response.json()
        return result.get("success", False)
    except Exception:
        return False