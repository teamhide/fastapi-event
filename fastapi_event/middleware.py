from starlette.types import ASGIApp, Receive, Scope, Send

from fastapi_event.handler import event_handler


class EventHandlerMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        try:
            with event_handler():
                await self.app(scope, receive, send)
        except Exception as e:
            raise e
