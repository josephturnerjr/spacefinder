import smtplib
from email.mime.text import MIMEText

FROM_EMAIL = "support@example.com"

TOKEN = {"subject": "Submit your nonprofit sublet",
                "content": """Follow the link below to submit your sublet space:

http://0.0.0.0:5000/submission/%(token)s"""}

def send_email(to_addr, subject, content, from_addr=FROM_EMAIL):
    recipients = [to_addr]
    msg = MIMEText(content)
    msg["Subject"] = subject
    msg['From'] = from_addr
    msg['To'] = ", ".join(recipients)
    c = smtplib.SMTP('localhost')
    c.sendmail(from_addr, recipients, msg.as_string())
    c.quit()


def send_token(to_addr, submission_token):
    return send_email(to_addr, TOKEN["subject"],
                      TOKEN["content"] % {"token": submission_token})
