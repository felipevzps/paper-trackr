import smtplib
import re
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from paper_trackr.config.global_settings import TEMPLATE_FILE, NEWSLETTER_OUTPUT

# read html template
def load_template(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

# generate the html body for each new paper found in a specific date
def generate_article_html(articles):
    html_parts = []

    for a in articles:
        abstract = a["abstract"].strip()
        # some abstracts startswith "Background", so im trying to avoid duplicates in the html template
        # by removing any html tags in the abstract, then checking if it startswith "Background", then adapting the template to deal with the abstract content for each paper
        clean_abstract = re.sub(r"<.*?>", "", abstract).strip()
        
        # include tldr
        tldr_html = ""

        if "tldr" in a and a["tldr"]:
            tldr_html = (
                f'<p style="font-size: 16px; text-align: justify; margin-bottom: 10px;">'
                f'<span style="font-weight: bold; font-size: 16px;">tl;dr:</span> {a["tldr"]}</p>'
            )

        # abstract 
        if clean_abstract.lower().startswith("background"):
            abstract_html = f'<p style="font-size: 16px; text-align: justify;">{abstract}</p>'
        else:
            abstract_html = (
                    '<p style="font-size: 16px; text-align: justify;">'
                    f'<span style="font-weight: bold; font-size: 16px;">Abstract:</span> {abstract}</p>' 
            )
        
        # merge tldr + abstract 
        formatted_abstract = tldr_html + abstract_html 

        article_html = f"""
            <div style="margin-bottom: 30px;">
                <h2 style="color: #000000; font-size: 22px;">{a["title"]}</h2>
                <p style="font-size: 14px; text-align: justify; margin-top: -10px; margin-bottom: 10px;"> {a["author"]}</p>
                
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="font-size:16px; margin-bottom: 12px;">
                    <tr>
                        <td align="left" style="font-style: italic;">
                            Source: {a["source"]}
                        </td>
                        <td align="right" style="font-style: italic;">
                            Published: {a["date"]}
                        </td>
                    </tr>
                </table>

                {formatted_abstract}
                <p><a href="{a["link"]}" style="color: #1a0dab; font-size: 16px;">Read full paper</a></p>
            </div>
            <hr style="border: none; border-top: 1px solid #ccc;">
        """
        html_parts.append(article_html)

    return "\n".join(html_parts)

# create updated html body
def compose_email_body(template_path, articles):
    today = datetime.now().strftime("%A, %d %B %Y")
    template = load_template(template_path)
    articles_html = generate_article_html(articles)
    return template.replace("{{ date }}", today).replace("{{ articles_html }}", articles_html)

# send newsletter email with new papers
def send_email(articles, sender_email, receiver_email, password):
    if not articles:
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Your daily dose of research is here - See what's new!"
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["X-Entity-Ref-ID"] = "null" # avoid grouping/threading emails by gmail (each email should apper as a new email, even if it has the same subject)

    html_body = compose_email_body(TEMPLATE_FILE, articles)
    msg.attach(MIMEText(html_body, "html"))
     
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())

# save newsletter html using template
def save_newsletter_html(articles):
    html_body = compose_email_body(TEMPLATE_FILE, articles)
    NEWSLETTER_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    print(f"Saving html to {NEWSLETTER_OUTPUT}")
    with open(NEWSLETTER_OUTPUT, "w", encoding="utf-8") as f:
        f.write(html_body)
