import questionary
import yaml
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "../config/accounts.yml")

def configure_email_accounts():
    print("Welcome to paper-trackr email configuration")

    # verify if accounts.yaml exists
    if os.path.exists(CONFIG_PATH):
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
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        yaml.dump(config, f)

    print(f"Configuration saved to {CONFIG_PATH}")
