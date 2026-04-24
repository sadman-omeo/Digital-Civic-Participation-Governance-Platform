import os
import requests


def send_brevo_email(to_email, to_name, subject, message):
    api_key = os.getenv("BREVO_API_KEY")
    sender_email = os.getenv("BREVO_SENDER_EMAIL")
    sender_name = os.getenv("BREVO_SENDER_NAME", "Digital Civic Platform")

    print("BREVO DEBUG -> api_key exists:", bool(api_key))
    print("BREVO DEBUG -> sender_email:", sender_email)
    print("BREVO DEBUG -> to_email:", to_email)

    if not api_key or not sender_email or not to_email:
        print("BREVO ERROR -> Missing email configuration")
        return False, "Missing email configuration"

    url = "https://api.brevo.com/v3/smtp/email"

    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json"
    }

    payload = {
        "sender": {
            "name": sender_name,
            "email": sender_email
        },
        "to": [
            {
                "email": to_email,
                "name": to_name or "User"
            }
        ],
        "subject": subject,
        "htmlContent": f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                <h2>{subject}</h2>
                <p>{message}</p>
                <hr>
                <p style="color: #666; font-size: 13px;">
                    Digital Civic Participation & Governance Platform
                </p>
            </body>
        </html>
        """
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)

        print("BREVO DEBUG -> status code:", response.status_code)
        print("BREVO DEBUG -> response text:", response.text)

        if response.status_code in [200, 201, 202]:
            return True, response.json() if response.text else {}
        return False, response.text

    except Exception as e:
        print("BREVO ERROR -> exception:", str(e))
        return False, str(e)
