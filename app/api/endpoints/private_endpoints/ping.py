from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

router = APIRouter(tags=["default"])


@router.get("/ping")
async def pong():
    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "PROOOOOOOOOOOOOOOOOD"})