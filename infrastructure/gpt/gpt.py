from typing import Optional, Dict, Any
from openai import OpenAI
from domain.repository.gpt import GptRepository
from domain.model.gpt import MODEL, CHARACTER_SETTINGS
import logging

logger = logging.getLogger(__name__)

class GptClient(GptRepository):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = OpenAI(api_key=self.api_key)

    async def create_completion(self, prompt: str) -> Optional[Dict[str, Any]]:
        try:
            response = self.client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": CHARACTER_SETTINGS},
                    {"role": "user", "content": prompt}
                ],
            )
            completion = response
            return completion
        except Exception as e:
            logger.error(f"Failed self.client.chat.completions.create: {e}")
            return None
