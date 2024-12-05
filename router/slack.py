from fastapi import APIRouter, HTTPException, Request
from interfaces.slack import SlackHandler

router = APIRouter(
    tags=["slack"],
    responses={404: {"description": "Not found"}},
)

def create_slack_router(slack_handler: SlackHandler) -> APIRouter:
    @router.post("/events")
    async def post_event(request: Request):
        try:
            return await slack_handler.handle_event(request)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    return router
