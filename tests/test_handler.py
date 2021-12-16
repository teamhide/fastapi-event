import pytest
from pydantic import BaseModel

from fastapi_event import event_handler, BaseEvent
from fastapi_event.exceptions import (
    InvalidEventTypeException,
    InvalidParameterTypeException,
    ParameterCountException,
    RequiredParameterException,
)


class TestEvent(BaseEvent):
    __test__ = False

    async def run(self, parameter=None) -> None:
        pass


class TestEventParameter(BaseModel):
    __test__ = False

    content: str


class TestEventDoNotHaveParameter(BaseEvent):
    __test__ = False

    async def run(self):
        pass


class TestEventParameterNotNone(BaseEvent):
    __test__ = False

    async def run(self, parameter):
        pass


@pytest.mark.asyncio
async def test_store_without_parameter(app_with_middleware, client):
    app = app_with_middleware

    async def test():
        await event_handler.store(
            event=TestEvent
        )
        handler = event_handler._get_event_handler()
        assert TestEvent in handler.events
        assert handler.events[TestEvent] is None

    @app.get("/")
    async def get():
        await test()

    client.get("/")


@pytest.mark.asyncio
async def test_store_with_parameter(app_with_middleware, client):
    app = app_with_middleware

    async def test():
        await event_handler.store(
            event=TestEvent,
            parameter=TestEventParameter(content="content"),
        )
        handler = event_handler._get_event_handler()
        assert TestEvent in handler.events
        assert isinstance(handler.events[TestEvent], TestEventParameter)

    @app.get("/")
    async def get():
        await test()

    client.get("/")


@pytest.mark.asyncio
async def test_store_with_invalid_event_type_exception(app_with_middleware, client):
    app = app_with_middleware

    class InvalidTypeEvent:
        pass

    async def test():
        with pytest.raises(InvalidEventTypeException):
            await event_handler.store(
                event=InvalidTypeEvent
            )

    @app.get("/")
    async def get():
        await test()

    client.get("/")


@pytest.mark.asyncio
async def test_store_with_invalid_parameter_type_exception(app_with_middleware, client):
    app = app_with_middleware

    async def test():
        with pytest.raises(InvalidParameterTypeException):
            await event_handler.store(
                event=TestEvent,
                parameter="a",
            )

    @app.get("/")
    async def get():
        await test()

    client.get("/")


@pytest.mark.asyncio
async def test_store_with_invalid_parameter_count_exception(app_with_middleware, client):
    app = app_with_middleware

    async def test():
        with pytest.raises(ParameterCountException):
            await event_handler.store(
                event=TestEventDoNotHaveParameter,
            )

    @app.get("/")
    async def get():
        await test()

    client.get("/")


@pytest.mark.asyncio
async def test_store_with_required_parameter_exception(app_with_middleware, client):
    app = app_with_middleware

    async def test():
        with pytest.raises(RequiredParameterException):
            await event_handler.store(
                event=TestEventParameterNotNone,
            )

    @app.get("/")
    async def get():
        await test()

    client.get("/")
