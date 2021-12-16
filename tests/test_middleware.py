from fastapi import FastAPI

from fastapi_event import EventHandlerMiddleware


def test_init(app: FastAPI):
    app.add_middleware(EventHandlerMiddleware)

    is_exist = False
    for middleware in app.user_middleware:
        if issubclass(middleware.cls, EventHandlerMiddleware):
            is_exist = True

    assert is_exist is True


def test_middleware_set_context_properly(app_with_middleware, client):
    app = app_with_middleware

    @app.get("/")
    async def test_get():
        from fastapi_event.handler import EventHandler, _handler_context  # noqa
        assert isinstance(_handler_context.get(), EventHandler)

    client.get("/")


def test_middleware_does_not_set_context(app, client):
    @app.get("/")
    async def test_get():
        from fastapi_event.handler import EventHandler, _handler_context  # noqa
        assert _handler_context.get() is None

    client.get("/")
