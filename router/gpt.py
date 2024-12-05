from fastapi import APIRouter, HTTPException
from interfaces.gpt import GptHandler

router = APIRouter(
    prefix="/gpt",
    tags=["gpt"],
    responses={404: {"description": "Not found"}},
)

def create_gpt_router(gpt_handler: GptHandler) -> APIRouter:
    @router.get("/")
    async def get_gpt(prompt: str):
        try:
            return await gpt_handler.create_completion(prompt)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    return router
