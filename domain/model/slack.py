from pydantic import BaseModel
from typing import List, Dict

# 読み込むメッセージの最大件数
DEFAULT_MAX_MESSAGES = 20

class SlackMessage(BaseModel):
    text: str  # メッセージの内容
    user: str  # メッセージを送信したユーザーのID

    def optimize_message(self, bot_user_id: str) -> str:
        """
        メッセージを整形し、ボットユーザーIDを置き換え
        """
        text = self.text.replace(bot_user_id, "[GptBot]").strip()
        return self._format_message(text)

    @staticmethod
    def _format_message(text: str) -> str:
        """
        メッセージ内の改行をスペースに置き換え
        """
        return text.replace("\n", " ")


class SlackMessages(BaseModel):
    messages: List[SlackMessage]

    def extract_conversation_flow(self, bot_user_id: str) -> List[Dict[str, str]]:
        """
        メッセージを整形し、会話フローを抽出
        """
        flow = []
        for message in self.messages:
            flow.append({
                "speaker": message.user,
                "message": message.optimize_message(bot_user_id),
            })
        return flow

    def limit_messages(self, max_messages: int) -> "SlackMessages":
        """
        メッセージを最大件数に制限
        """
        limited_messages = self.messages[-max_messages:]
        return SlackMessages(messages=limited_messages)

    def create_prompt(self, bot_user_id: str, max_messages: int = DEFAULT_MAX_MESSAGES) -> str:
        """
        プロンプトを生成
        """
        limited_messages = self.limit_messages(max_messages)
        builder = ["以下はSlackスレッドの履歴を含んだGPTプロンプトです。下記を踏まえて答えてください\n"]
        for flow in limited_messages.extract_conversation_flow(bot_user_id):
            builder.append(f'{flow["speaker"]}, message: {flow["message"]}\n')
        return "".join(builder)


def convert_to_slack_messages(slack_messages: List[Dict[str, str]]) -> SlackMessages:
    """
    SlackのメッセージをSlackMessagesに変換
    """
    messages = [SlackMessage(text=msg["text"], user=msg["user"]) for msg in slack_messages]
    return SlackMessages(messages=messages)
