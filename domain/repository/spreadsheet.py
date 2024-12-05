from abc import ABC, abstractmethod
from typing import Optional
from domain.model.spreadsheet import SpreadsheetData


class SpreadsheetRepository(ABC):
    @abstractmethod
    async def get_spreadsheet_data_by_slack_id(self, user_id: str) -> Optional[SpreadsheetData]:
        pass

    @abstractmethod
    async def update_spreadsheet(self, update: SpreadsheetData) -> None:
        pass
