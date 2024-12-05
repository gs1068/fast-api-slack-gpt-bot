from fastapi import FastAPI
import uvicorn
import logging
from config.load_env import Config
from infrastructure.gpt.gpt import GptClient
from infrastructure.slack.slack import SlackClient
from infrastructure.spreadsheet.spreadsheet import SpreadsheetClient
from usecase.gpt import GptUsecase
from usecase.slack import SlackUsecase
from interfaces.gpt import GptHandler
from interfaces.slack import SlackHandler
from router.gpt import create_gpt_router
from router.slack import create_slack_router
from router.ping import router as ping_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Slack GPT Bot API",
    description="This is a Slack GPT bot built with FastAPI using DDD principles.",
    version="1.0.0"
)

@app.on_event("startup")
async def on_startup():
    """アプリケーション起動時の処理"""
    logger.info("Starting Slack GPT Bot API...")
    try:
        # 環境変数の検証とGoogle認証情報のロード
        Config.validate()
        Config.load_google_credentials()
        logger.info("Environment variables and Google credentials successfully validated.")

        # Infrastructure
        app.state.gpt_client = GptClient(api_key=Config.OPENAI_API_KEY)
        app.state.slack_client = SlackClient(slack_token=Config.SLACK_BOT_TOKEN)
        app.state.spreadsheet_client = SpreadsheetClient(
            spreadsheet_id=Config.SPREADSHEET_ID,
            credentials=Config.CREDENTIALS
        )

        # Usecase
        app.state.gpt_usecase = GptUsecase(app.state.gpt_client)
        app.state.slack_usecase = SlackUsecase(
            app.state.slack_client,
            app.state.gpt_client,
            app.state.spreadsheet_client
        )

        # Interfaces
        gpt_handler = GptHandler(app.state.gpt_usecase)
        slack_handler = SlackHandler(app.state.slack_usecase)

        # Routers
        app.include_router(create_gpt_router(gpt_handler))
        app.include_router(create_slack_router(slack_handler))
        app.include_router(ping_router)

        logger.info("Slack GPT Bot API successfully started.")
    except Exception as e:
        logger.error(f"Failed to initialize app during startup: {e}")
        raise RuntimeError("Application startup failed.")


@app.on_event("shutdown")
async def on_shutdown():
    logger.info("Shutting down Slack GPT Bot API...")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
