import smtplib
import re
import os
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_TEMPLATE = os.path.join(BASE_DIR, "../templates/newsletter_template.html")

def load_template(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def generate_article_html(articles):
    html_parts = []

    for a in articles:
        abstract = a["abstract"].strip()
        # some abstracts startswith "Background", so im trying to avoid duplicates in the html template
        # by removing any html tags in the abstract, then checking if it startswith "Background", then adapting the template to deal with the abstract content for each paper
        clean_abstract = re.sub(r"<.*?>", "", abstract).strip()

        if clean_abstract.lower().startswith("background"):
            formatted_abstract = f'<p style="font-size: 16px; text-align: justify;">{abstract}</p>'
        else:
            formatted_abstract = (
                    '<h4 style="margin-bottom: 5px;">Background</h4>'
                    f'<p style="font-size: 16px; text-align: justify;">{abstract}</p>'
            )

        article_html = f"""
            <div style="margin-bottom: 30px;">
                <h2 style="color: #000000; font-size: 22px;">{a["title"]}</h2>
                <p style="font-size: 16px;"><em>Source: {a["source"]}</em></p>
                {formatted_abstract}
                <p><a href="{a["link"]}" style="color: #1a0dab; font-size: 16px;">Read full paper</a></p>
            </div>
            <hr style="border: none; border-top: 1px solid #ccc;">
        """
        html_parts.append(article_html)

    return "\n".join(html_parts)

def compose_email_body(template_path, articles):
    today = datetime.now().strftime("%A, %d %B %Y")
    template = load_template(template_path)
    articles_html = generate_article_html(articles)
    return template.replace("{{ date }}", today).replace("{{ articles_html }}", articles_html)

def send_email(articles, sender_email, receiver_email, password):
    if not articles:
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Your daily dose of research is here - See what's new!"
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["X-Entity-Ref-ID"] = "null" # avoid grouping/threading emails by gmail (each email should apper as a new email, even if it has the same subject)

    html_body = compose_email_body(HTML_TEMPLATE, articles)
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
