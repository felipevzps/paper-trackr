import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(articles, sender_email, receiver_email, password):
    if not articles:
        return

    msg = MIMEMultipart()
    msg['Subject'] = "Your daily dose of research is here - See what's new!"
    msg['From'] = sender_email
    msg['To'] = receiver_email
    # avoid grouping/threading emails
    msg['X-Entity-Ref-ID'] = 'null'
    body = ""
    for a in articles:
        body += f"<p><b>{a['title']}</b><br><a href='{a['link']}'>{a['link']}</a><br>Source: {a['source']}</p><hr>"

    msg.attach(MIMEText(body, 'html'))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
