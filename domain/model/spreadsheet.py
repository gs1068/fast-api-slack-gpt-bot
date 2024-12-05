from pydantic import BaseModel, Field
from datetime import datetime, timedelta, timezone
from dateutil.parser import isoparse
from typing import Optional
import logging

DAILY_TOKEN_LIMIT = 20000
JST = timezone(timedelta(hours=9), "Asia/Tokyo")

class SpreadsheetData(BaseModel):
    user_id: str = Field(..., alias="UserID")
    total_usage: int = Field(0, alias="TotalUsage")
    last_used_at: Optional[str] = Field(None, alias="LastUsedAt")
    tokens_usage: int = Field(0, alias="TokensUsage")
    daily_tokens_usage: int = Field(0, alias="DailyTokensUsage")
    total_tokens_usage: int = Field(0, alias="TotalTokensUsage")

    def can_use_daily_tokens(self) -> None:
        """
        毎日のトークン使用量が制限を超えているかを確認
        """
        logging.info(f"トークン使用量: {self.daily_tokens_usage}")
        if self.daily_tokens_usage > DAILY_TOKEN_LIMIT:
            raise ValueError("Daily token limit exceeded.")

    def add_token_usage(self, tokens: int) -> None:
        """
        トークン使用量を追加
        """
        self.total_usage += 1
        self.daily_tokens_usage += tokens
        self.total_tokens_usage += tokens

    def reset_daily_usage_if_needed(self) -> None:
        """
        必要に応じて1日の使用量をリセット
        """
        now = datetime.now(JST)
        now_date = now.strftime("%Y-%m-%d")

        if self.last_used_at:
            try:
                last_used_time = isoparse(self.last_used_at)
                last_used_date = last_used_time.astimezone(JST).strftime("%Y-%m-%d")
                if last_used_date != now_date:
                    self.daily_tokens_usage = 0
            except ValueError as e:
                logging.error(f"Failed to parse last_used_at: {self.last_used_at}, Error: {e}")
                self.daily_tokens_usage = 0

        # 現在時刻を更新
        self.last_used_at = now.isoformat()

    @classmethod
    def create_new(cls, user_id: str) -> "SpreadsheetData":
        """
        新しいスプレッドシートデータを生成
        """
        return cls.construct(
            user_id=user_id,
            total_usage=0,
            last_used_at=None,
            tokens_usage=0,
            daily_tokens_usage=0,
            total_tokens_usage=0,
        )
