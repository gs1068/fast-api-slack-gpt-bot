from domain.repository.gpt import GptRepository
import logging

logger = logging.getLogger(__name__)

class GptUsecase:
    def __init__(self, gpt_repository: GptRepository):
        self.gpt_repository = gpt_repository

    async def generate_text(self, prompt: str) -> str:
        try:
            res = await self.gpt_repository.create_completion(prompt)
            return res.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Failed self.gpt_repository.create_completion: {e}")
            return None
