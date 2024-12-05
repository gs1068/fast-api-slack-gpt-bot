from fastapi import HTTPException
from usecase.gpt import GptUsecase
import logging

logger = logging.getLogger(__name__)

class GptHandler:
    def __init__(self, gpt_usecase: GptUsecase):
        self.gpt_usecase = gpt_usecase

    async def create_completion(self, prompt: str):
        try:
            result = await self.gpt_usecase.generate_text(prompt)
            if result is None:
                raise HTTPException(status_code=500, detail="Failed self.gpt_usecase.generate_text")
            return result
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Failed self.gpt_usecase.generate_text: {e}")
            raise HTTPException(status_code=500, detail="Unexpected error occurred.")
