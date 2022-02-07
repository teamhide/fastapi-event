from fastapi import Request
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)

from fastapi_event.handler import event_handler


class EventHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ):
        try:
            with event_handler():
                response = await call_next(request)
        except Exception as e:
            raise e from None

        return response
