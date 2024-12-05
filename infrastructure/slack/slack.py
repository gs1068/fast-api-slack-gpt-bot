from typing import List
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError
from domain.repository.slack import SlackRepository
from domain.model.slack import SlackMessage


class SlackClient(SlackRepository):
    def __init__(self, slack_token: str):
        self.slack_client = AsyncWebClient(token=slack_token)

    async def load_conversation_replies(self, channel_id: str, timestamp: str) -> List[SlackMessage]:
        """指定したメッセージのスレッド内の返信を取得"""
        messages = []
        cursor = None

        try:
            while True:
                response = await self.slack_client.conversations_replies(
                    channel=channel_id,
                    ts=timestamp,
                    cursor=cursor
                )
                messages.extend(response.get("messages", []))
                cursor = response.get("response_metadata", {}).get("next_cursor", None)

                if not cursor:
                    break
            return messages
        except SlackApiError as e:
            raise RuntimeError(f"Failed self.slack_client.conversations_replies: {e.response['error']}")

    async def get_bot_user_id(self) -> str:
        """SlackボットのユーザーIDを取得"""
        try:
            response = await self.slack_client.auth_test()
            return response.get("user_id", "")
        except SlackApiError as e:
            raise RuntimeError(f"Failed self.slack_client.auth_test: {e.response['error']}")

    async def create_new_message(self, channel_id: str, timestamp: str, message: str) -> None:
        """ボットによる新しいメッセージを作成"""
        try:
            await self.slack_client.chat_postMessage(
                channel=channel_id,
                text=message,
                thread_ts=timestamp
            )
        except SlackApiError as e:
            raise RuntimeError(f"Failed self.slack_client.chat_postMessage: {e.response['error']}")
