import os
import requests
import logging

VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"


def verify_recaptcha(recaptcha_response: str) -> bool:
    """Verify a Google reCAPTCHA response token.

    Behavior:
    - Reads secret from `RECAPTCHA_SECRET_KEY` environment variable.
    - If `RECAPTCHA_DISABLED` is set (truthy), verification is bypassed (useful for local dev).
    - Returns True only when Google reports success.
    """
    # Allow an explicit bypass for local development/testing
    if os.getenv("RECAPTCHA_DISABLED", "0") in ("1", "true", "True"):
        logging.getLogger(__name__).warning("reCAPTCHA disabled via RECAPTCHA_DISABLED env var — bypassing verification")
        return True

    secret_key = os.getenv("RECAPTCHA_SECRET_KEY")

    if not secret_key:
        logging.getLogger(__name__).warning("RECAPTCHA_SECRET_KEY not set — rejecting verification")
        return False

    if not recaptcha_response:
        logging.getLogger(__name__).info("No reCAPTCHA response token provided")
        return False

    data = {
        "secret": secret_key,
        "response": recaptcha_response
    }

    try:
        resp = requests.post(VERIFY_URL, data=data, timeout=5)
        resp.raise_for_status()
        result = resp.json()
        success = bool(result.get("success", False))
        if not success:
            logging.getLogger(__name__).info("reCAPTCHA verification failed: %s", result)
        return success
    except requests.RequestException as e:
        logging.getLogger(__name__).exception("reCAPTCHA request failed: %s", e)
        return False