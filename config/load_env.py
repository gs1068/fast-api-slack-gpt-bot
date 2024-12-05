import os
from dotenv import load_dotenv
from google.oauth2 import service_account
import logging

logger = logging.getLogger(__name__)

load_dotenv()

class Config:
    SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
    GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH")
    CREDENTIALS = None

    @staticmethod
    def validate():
        required_vars = ["SLACK_BOT_TOKEN", "OPENAI_API_KEY", "SPREADSHEET_ID", "GOOGLE_CREDENTIALS_PATH"]
        missing_vars = [var for var in required_vars if not getattr(Config, var)]
        if missing_vars:
            raise RuntimeError(f"Missing required environment variables: {', '.join(missing_vars)}")

    @staticmethod
    def load_google_credentials():
        try:
            credentials_path = Config.GOOGLE_CREDENTIALS_PATH
            logger.info(f"Attempting to load Google credentials from: {credentials_path}")

            if not os.path.exists(credentials_path):
                raise FileNotFoundError(f"Google credentials file not found at {credentials_path}")

            Config.CREDENTIALS = service_account.Credentials.from_service_account_file(
                credentials_path,
                scopes=["https://www.googleapis.com/auth/spreadsheets"]
            )
            logger.info("Google credentials successfully loaded.")
        except Exception as e:
            logger.error(f"Failed to load Google credentials: {e}")
            raise RuntimeError("Failed to load Google credentials.")
