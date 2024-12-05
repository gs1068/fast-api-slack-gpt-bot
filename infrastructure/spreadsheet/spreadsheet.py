import logging
from pydantic import ValidationError
from typing import Optional, List, Dict, Any
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from domain.repository.spreadsheet import SpreadsheetRepository
from domain.model.spreadsheet import SpreadsheetData

logger = logging.getLogger(__name__)

DATA_RANGE = "Activity!A:E"

class SpreadsheetClient(SpreadsheetRepository):
    def __init__(self, spreadsheet_id: str, credentials):
        """
        Google Sheets APIクライアントを初期化
        """
        if not credentials:
            raise ValueError("Google credentials must be provided.")
        self.spreadsheet_id = spreadsheet_id
        self.service = build("sheets", "v4", credentials=credentials)

    async def get_spreadsheet_data_by_slack_id(self, user_id: str) -> Optional[SpreadsheetData]:
        """
        SlackユーザーIDに基づいてスプレッドシートデータを取得
        """
        try:
            values = await self._read_spreadsheet(DATA_RANGE)

            for row in values:
                if len(row) < 5 or not all(row[:5]):
                    logger.warning(f"Invalid row detected: {row}")
                    continue

                if row[0] == user_id:
                    try:
                        return SpreadsheetData.construct(
                            user_id=row[0],
                            total_usage=int(row[1]),
                            last_used_at=row[2] if row[2] else None,
                            tokens_usage=int(row[3]),
                            daily_tokens_usage=int(row[4]),
                            total_tokens_usage=int(row[3]),
                        )
                    except ValidationError as e:
                        logger.error(f"Error parsing row: {row}, Error: {e}")
        except HttpError as e:
            logger.error(f"Error reading spreadsheet: {e}")
        except Exception as e:
            logger.error(f"Failed to get spreadsheet data: {e}")
        return None

    async def update_spreadsheet(self, update: SpreadsheetData) -> None:
        """
        スプレッドシートのデータを更新
        """
        try:
            values = await self._read_spreadsheet(DATA_RANGE)
            user_data = self._map_spreadsheet_data(values)
            now = self._get_current_time()

            user_data[update.user_id] = self._convert_activity_data(update, now)
            updated_values = self._map_to_sorted_slice(user_data)

            await self._write_spreadsheet(DATA_RANGE, updated_values)
        except HttpError as e:
            logger.error(f"Error updating spreadsheet: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to update spreadsheet: {e}")
            raise

    async def _read_spreadsheet(self, read_range: str) -> List[List[Any]]:
        """
        スプレッドシートからデータを読み取る
        """
        try:
            sheet = self.service.spreadsheets()
            result = sheet.values().get(
                spreadsheetId=self.spreadsheet_id,
                range=read_range,
            ).execute()
            return result.get("values", [])
        except Exception as e:
            logger.error(f"Failed to read spreadsheet: {e}")
            raise

    async def _write_spreadsheet(self, write_range: str, values: List[List[Any]]) -> None:
        """
        スプレッドシートにデータを書き込む
        """
        try:
            sheet = self.service.spreadsheets()
            body = {"values": values}
            sheet.values().update(
                spreadsheetId=self.spreadsheet_id,
                range=write_range,
                valueInputOption="RAW",
                body=body,
            ).execute()
        except Exception as e:
            logger.error(f"Failed to write spreadsheet: {e}")
            raise

    def _map_spreadsheet_data(self, values: List[List[Any]]) -> Dict[str, List[Any]]:
        """
        スプレッドシートデータを辞書形式にマッピング
        """
        user_data = {}
        for row in values:
            if len(row) < 5:
                continue
            user_id = row[0]
            user_data[user_id] = row
        return user_data

    def _convert_activity_data(self, update: SpreadsheetData, now: str) -> List[Any]:
        """
        更新データをスプレッドシート用フォーマットに変換
        """
        return [
            update.user_id,
            str(update.total_usage),
            now,
            str(update.total_tokens_usage),
            str(update.daily_tokens_usage),
        ]

    def _map_to_sorted_slice(self, user_data: Dict[str, List[Any]]) -> List[List[Any]]:
        """
        ユーザーデータをソート済みのリスト形式に変換
        """
        sorted_data = sorted(user_data.values(), key=lambda x: x[0])
        return sorted_data

    def _get_current_time(self) -> str:
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()
