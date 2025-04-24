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

# scitldr paths
SCITLDR_DIR = BASE_DIR / "scitldr"
SCITLDR_DATA_DIR = SCITLDR_DIR / "data"
SCITLDR_MODEL_DIR = SCITLDR_DIR / "model"
SCITLDR_OUT_DIR = SCITLDR_DIR / "tldr"
SCITLDR_DATA_SUBDIR = SCITLDR_DATA_DIR / "paper-trackr_abstracts"
SCITLDR_SOURCE_FILE = "paper-trackr_abstracts.source" 
SCITLDR_TEST_FILE = "paper-trackr.tldr"
SCITLDR_BART_XSUM = "scitldr_bart-xsum.tldr-ao.pt"

# scitldr optimal decoder params for paper-trackr
BEAM_SIZE = "2"
LENGTH_PENALTY = "1"
MAX_LENGTH = "60"
MIN_LENGTH = "10"
