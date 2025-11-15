import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
DB_URL = os.getenv("DB_URL", "sqlite:///players.db")
SQL_ECHO = os.getenv("SQL_ECHO", "0") == "1"

if not BOT_TOKEN:
    raise RuntimeError(
        "BOT_TOKEN is not set. Put it into .env or environment.")
