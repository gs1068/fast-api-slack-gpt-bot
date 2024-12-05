from abc import ABC, abstractmethod

class GptRepository(ABC):
    @abstractmethod
    async def create_completion(self, prompt: str) -> any:
        pass
