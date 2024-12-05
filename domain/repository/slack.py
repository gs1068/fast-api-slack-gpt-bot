from abc import ABC, abstractmethod
from domain.model.slack import SlackMessage
from typing import List

class SlackRepository(ABC):
  @abstractmethod
  async def load_conversation_replies(self, channelID: str, timestamp: str, test: str) -> List[SlackMessage]:
    pass
  @abstractmethod
  async def create_new_message(self, channel_id: str, timestamp: str, message: str) -> None:
    pass
  @abstractmethod
  async def get_bot_user_id(self) -> str:
    pass
