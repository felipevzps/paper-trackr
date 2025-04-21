import yaml
import questionary
from pathlib import Path
from paper_trackr.config.global_settings import ACCOUNTS_FILE

# configure sender and receiver emails 
def configure_email_accounts():
    print("Welcome to paper-trackr email configuration")

    # verify if accounts.yaml exists
    if Path(ACCOUNTS_FILE).exists():
        overwrite = questionary.confirm("An existing config was found. Overwrite?").ask()
        if not overwrite:
            print("Configuration canceled.")
            return

    # configure user emails 
    sender_email = questionary.text("Enter sender email:").ask()
    sender_password = questionary.password("Enter sender password (Google App Password):").ask()
    receivers = questionary.text("Enter receiver emails (comma-separated):").ask()

    # create yaml structure
    receiver_list = [{'email': r.strip()} for r in receivers.split(",")]

    config = {
        'sender': {
            'email': sender_email,
            'password': sender_password
        },
        'receiver': receiver_list
    }

    # save configuration 
    ACCOUNTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(ACCOUNTS_FILE, "w") as f:
        yaml.dump(config, f)

    print(f"Configuration saved to {ACCOUNTS_FILE}")
