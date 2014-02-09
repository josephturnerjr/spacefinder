from spacefinder import app
import requests

FROM_EMAIL = "Maryland Nonprofits <support@%s>" % app.config['DOMAIN']

TOKEN = {
    "subject": "Submit your nonprofit space",
    "content": """Thanks for signing up to post your space on Maryland Nonprofits' Space Finder. This is Step 2 of a 4-step process. The link provided in this email is the only way to edit your listing in the future - be sure to save it.

Please submit listings for space only if the space is located within the state of Maryland and appropriate for use by a nonprofit organization. Please do not list residential spaces unless appropriately zoned for commercial use. To complete your submission, click on the link below.

http://%(domain)s/submission/%(token)s

If the link doesn't work, please copy and paste it into your browser window.

Maryland Nonprofits derives no fee or benefit by facilitating this transaction. We provide this service as a courtesy to our members and sector friends in furtherance of our mission.

Thanks again,
Maryland Nonprofits
1500 Union Ave, Suite 2500
Baltimore, MD 21211
(410) 727-6367 x2346
Fax: (410) 235-2190
http://www.marylandnonprofits.org
""",
    "html_content": """<html><p>Thanks for signing up to post your space on Maryland Nonprofits' Space Finder. This is Step 2 of a 4-step process. The link provided in this email is the only way to edit your listing in the future - be sure to save it.</p>

<p>Please submit listings for space only if the space is located within the state of Maryland and appropriate for use by a nonprofit organization. Please do not list residential spaces unless appropriately zoned for commercial use. To complete your submission, click on the link below.</p>

<p><a href='http://%(domain)s/submission/%(token)s'>http://%(domain)s/submission/%(token)s</a></p>

<p>If the link doesn't work, please copy and paste it into your browser window.</p>

<p>Maryland Nonprofits derives no fee or benefit by facilitating this transaction. We provide this service as a courtesy to our members and sector friends in furtherance of our mission.</p>

<p>
Thanks again,<br />
Maryland Nonprofits<br />
1500 Union Ave, Suite 2500<br />
Baltimore, MD 21211<br />
(410) 727-6367 x2346<br />
Fax: (410) 235-2190<br />
<a href='http://www.marylandnonprofits.org'><img src='cid:inline-logo.jpg' /></a></p></html>
"""}


def send_email(to_addr, subject, content, html_content=None, from_addr=FROM_EMAIL):
    data = {"from": from_addr,
            "to": [to_addr],
            "subject": subject,
            "text": content}
    if html_content:
        data['html'] = html_content
        
    r = requests.post(
        "https://api.mailgun.net/v2/%s/messages" % app.config.get('MAILGUN_DOMAIN', app.config['DOMAIN']),
        files=[("inline", open("spacefinder/static/img/inline-logo.jpg"))],
        auth=("api", app.config['MAILGUN_API_KEY']),
        data=data)
    print r.status_code
    print r.text
    return r


def send_token(to_addr, submission_token):
    return send_email(to_addr,
                      TOKEN["subject"],
                      TOKEN["content"] % {"token": submission_token,
                                          "domain": app.config["DOMAIN"]},
                      html_content=TOKEN["html_content"] % {"token": submission_token,
                                          "domain": app.config["DOMAIN"]})
