from spacefinder import app
import requests

FROM_EMAIL = "Maryland Nonprofits <support@%s>" % app.config['DOMAIN']

TOKEN = {
    "subject": "Submit your nonprofit space",
    "content": """Follow the link below to submit your space:

http://%(domain)s/submission/%(token)s"""}


def send_email(to_addr, subject, content, from_addr=FROM_EMAIL):
    r = requests.post(
        "https://api.mailgun.net/v2/%s/messages" % app.config.get('MAILGUN_DOMAIN', app.config['DOMAIN']),
        auth=("api", app.config['MAILGUN_API_KEY']),
        data={"from": from_addr,
              "to": [to_addr],
              "subject": subject,
              "text": content})
    print r.status_code
    print r.text
    return r


def send_token(to_addr, submission_token):
    return send_email(to_addr,
                      TOKEN["subject"],
                      TOKEN["content"] % {"token": submission_token,
                                          "domain": app.config["DOMAIN"]})
