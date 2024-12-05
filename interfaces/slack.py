from fastapi import Request
from fastapi.responses import JSONResponse
from slack_sdk.errors import SlackApiError
from usecase.slack import SlackUsecase
import logging

logger = logging.getLogger(__name__)

class SlackHandler:
    def __init__(self, slack_usecase: SlackUsecase):
        self.slack_usecase = slack_usecase

    async def handle_event(self, request: Request):
        try:
            # リトライリクエストの処理
            retry_num = request.headers.get("X-Slack-Retry-Num")
            if retry_num:
                logger.info(f"Retry detected. Count: {retry_num}")
                return JSONResponse(content={"status": "ignored"}, status_code=200)

            # リクエストボディの読み取り
            event_data = await request.json()
            event = event_data.get("event", {})

            # イベントデータの抽出
            extracted_data = self.extract_event_data(event, event_data)

            # 無効なメッセージを無視
            if not extracted_data["user"] or extracted_data["bot_id"]:
                logger.info("Message from bot or invalid user. Ignoring.")
                return JSONResponse(content={"status": "no content"}, status_code=200)

            # イベントの処理
            return await self.process_event(extracted_data)

        except SlackApiError as e:
            error_detail = e.response.get('error', 'Unknown error')
            logger.error(f"Slack API Error: {error_detail}")
            return JSONResponse(
                content={"status": "error", "detail": f"Slack API Error: {error_detail}"},
                status_code=500,
            )
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            return JSONResponse(
                content={"status": "error", "detail": "Unexpected server error"},
                status_code=500,
            )

    def extract_event_data(self, event: dict, event_data: dict) -> dict:
        """イベントから必要なデータを抽出"""
        return {
            "event_type": event.get("type"),
            "user": event.get("user"),
            "bot_id": event.get("bot_id"),
            "channel": event.get("channel"),
            "timestamp": self.get_thread_timestamp(event.get("ts"), event.get("thread_ts")),
            "channel_type": event.get("channel_type"),
            "text": event.get("text", ""),
            "authorizations": event_data.get("authorizations", [{}]),
        }

    async def process_event(self, extracted_data: dict) -> JSONResponse:
        """イベントタイプに基づいて処理を実行"""
        event_type = extracted_data["event_type"]
        channel = extracted_data["channel"]
        timestamp = extracted_data["timestamp"]
        user = extracted_data["user"]
        text = extracted_data["text"]
        channel_type = extracted_data["channel_type"]

        # DMの場合、メンションがなくても処理する
        if channel_type == "im":
            logger.info(f"Processing direct message in channel {channel}.")
            await self.slack_usecase.process_messages(channel, timestamp, user)
            return JSONResponse(content={"status": "ok"}, status_code=200)

        # メンションが含まれていない場合、返信しない
        if f"<@{extracted_data['authorizations'][0].get('user_id')}>" not in text:
            logger.info(f"No mention detected in message. Ignoring message in channel {channel}.")
            return JSONResponse(content={"status": "no content"}, status_code=200)

        # app_mention の処理
        if event_type == "app_mention":
            logger.info(f"Processing app_mention in channel {channel}.")
            await self.slack_usecase.process_messages(channel, timestamp, user)
            return JSONResponse(content={"status": "ok"}, status_code=200)

        # その他のメッセージタイプは無視
        logger.info(f"Unsupported message event type: {event_type}, channel type: {channel_type}.")
        return JSONResponse(content={"status": "no content"}, status_code=200)

    @staticmethod
    def get_thread_timestamp(timestamp: str, thread_timestamp: str) -> str:
        """スレッドタイムスタンプの取得"""
        return thread_timestamp or timestamp
