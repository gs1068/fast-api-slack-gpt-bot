from domain.repository.gpt import GptRepository
from domain.repository.slack import SlackRepository
from domain.model.slack import SlackMessages
from domain.repository.spreadsheet import SpreadsheetRepository
from domain.model.spreadsheet import SpreadsheetData
import logging

logger = logging.getLogger(__name__)

class SlackUsecase:
    def __init__(
            self,
            slack_repository: SlackRepository,
            gpt_repository: GptRepository,
            spreadsheet_repository: SpreadsheetRepository
    ):
        self.gpt_repository = gpt_repository
        self.slack_repository = slack_repository
        self.spreadsheet_repository = spreadsheet_repository

    async def process_messages(self, channel_id: str, timestamp: str, user_id: str) -> None:
        try:
            # BotのユーザーIDを取得
            bot_user_id = await self.slack_repository.get_bot_user_id()
            if not bot_user_id:
                logger.error("Bot user ID not found.")
                return

            # スプレッドシートからデータを取得
            spreadsheet_data = await self.spreadsheet_repository.get_spreadsheet_data_by_slack_id(user_id)
            if not spreadsheet_data:
                # データがない場合は新しいデータを作成
                spreadsheet_data = SpreadsheetData.create_new(user_id)

            # 日付が変わったらトークン使用量をリセット
            spreadsheet_data.reset_daily_usage_if_needed()

            try:
                spreadsheet_data.can_use_daily_tokens()
            except ValueError:
                limit_message = "本日の利用制限を超えました。明日以降に再度お試しください。"
                await self.slack_repository.create_new_message(channel_id, timestamp, limit_message)
                return

            # Slackスレッド内の過去のメッセージを取得
            messages = await self.slack_repository.load_conversation_replies(channel_id, timestamp)
            if not messages:
                logger.error(f"No messages found for channel {channel_id} at timestamp {timestamp}.")
                return

            # Slackメッセージをモデルに変換
            slack_messages = SlackMessages(messages=messages)
            gpt_prompt = slack_messages.create_prompt(bot_user_id)

            logger.info(f"Processing messages: {gpt_prompt}")

            # GPTにプロンプトを送信して応答を取得
            gpt_response = await self.gpt_repository.create_completion(gpt_prompt)
            if not gpt_response or not gpt_response.choices:
                logger.error("GPT response is empty.")
                gpt_message = "GPTレスポンスが空です。"
            else:
                gpt_message = gpt_response.choices[0].message.content.strip()

            # SlackBot（GPT）の応答を送信
            await self.slack_repository.create_new_message(channel_id, timestamp, gpt_message)

            # 使用量を加算
            spreadsheet_data.add_token_usage(gpt_response.usage.total_tokens)
            await self.spreadsheet_repository.update_spreadsheet(spreadsheet_data)

        except Exception as e:
            logger.error(f"Failed to process messages: {e}")
            raise
