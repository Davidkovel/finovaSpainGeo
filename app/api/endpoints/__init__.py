from fastapi import APIRouter

from app.api.endpoints.private_endpoints import ping, user
from app.api.endpoints.public_endoints import auth

root_router = APIRouter()

sub_routers = (
    ping.router,
    auth.router,
    user.router,
)

for router in sub_routers:
    root_router.include_router(router)
