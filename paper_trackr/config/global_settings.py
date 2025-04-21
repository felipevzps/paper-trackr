from pathlib import Path 

# main.py directory
BASE_DIR = Path(__file__).resolve().parent.parent

# config directory
CONFIG_DIR = BASE_DIR / "config"
ACCOUNTS_FILE = CONFIG_DIR / "accounts.yml"
SEARCH_QUERIES_FILE = CONFIG_DIR / "search_queries.yml"

# database directory
DATABASE_DIR = BASE_DIR / "database"
DB_FILE = DATABASE_DIR / "articles.db"
HISTORY_FILE = DATABASE_DIR / "history.csv"

# template directory 
TEMPLATES_DIR = BASE_DIR / "templates"
TEMPLATE_FILE = TEMPLATES_DIR / "newsletter_template.html"

# newsletter directory
NEWSLETTER_OUTPUT = BASE_DIR / "newsletter" / "paper-trackr_newsletter.html"
