import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def send_email(articles, sender_email, receiver_email, password):
    if not articles:
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Your daily dose of research is here - See what's new!"
    msg["From"] = sender_email
    msg["To"] = receiver_email
    # avoid grouping/threading emails by gmail
    msg["X-Entity-Ref-ID"] = "null"

    today = datetime.now().strftime("%A, %d %B %Y")

    # begin html body
    html = f"""\
    <html>
    <head>
        <meta charset="UTF-8">
        <title>paper-trackr newsletter</title>
    </head>
    <body style="font-family: Georgia, serif; background-color: #f4f4f4; padding: 20px; font-size: 16px;">
        <div style="background-color: white; padding: 30px; max-width: 700px; margin: auto; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <h1 style="border-bottom: 2px solid #000000; font-size: 28px;">paper-trackr newsletter</h1>
            <p style="color: gray; font-size: 16px;"><strong>{today}</strong></p>
            <p style="font-size: 16px;">Hello science reader,</p>
            <p style="font-size: 16px;">Welcome to your daily dose of research. Dive into the latest discoveries from the world of science!</p>
            <hr style="margin: 20px 0;">
    """

    for a in articles:
        abstract = a["abstract"].strip()
        # some abstracts startswith "Background", so lets avoid duplicates in the html template
        # remove any html in the abstracts and check if it startswith "Background"
        clean_abstract = re.sub(r"<.*?>", "", abstract).strip()

        if clean_abstract.lower().startswith("background"):
            formatted_abstract = f'<p style="font-size: 16px;">{abstract}</p>'
        else:
            formatted_abstract = f'<p style="font-size: 16px;"><h4>Background</h4>{abstract}</p>'

        html += f"""\
            <div style="margin-bottom: 30px;">
                <h2 style="color: #000000; font-size: 22px;">{a["title"]}</h2>
                <p style="font-size: 16px;"><em>Source: {a["source"]}</em></p>
                {formatted_abstract}
                <p><a href="{a["link"]}" style="color: #1a0dab; font-size: 16px;">Read full paper</a></p>
            </div>
            <hr style="border: none; border-top: 1px solid #ccc;">
        """

    html += """\
            <p style="font-size: 14px; color: gray;">
                You"re receiving this email because you subscribed to
                <a href="https://github.com/felipevzps/paper-trackr" style="color: #1a0dab; text-decoration: none;">paper-trackr</a>.
                Stay curious!
            </p>
        </div>
    </body>
    </html>
    """

    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
