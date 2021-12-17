import pytest

from fastapi_event import event_handler
from fastapi_event.exceptions import (
    InvalidEventTypeException,
    InvalidParameterTypeException,
    ParameterCountException,
    RequiredParameterException,
)
from tests.events import (
    TestSecondEvent,
    TestEventParameterNotNone,
    TestEvent,
    TestEventDoNotHaveParameter,
    TestEventParameter,
)


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
async def test_multiple_store_without_parameter(app_with_middleware, client):
    app = app_with_middleware

    async def test():
        await event_handler.store(
            event=TestEvent
        )
        await event_handler.store(
            event=TestSecondEvent
        )
        handler = event_handler._get_event_handler()
        assert len(handler.events) == 2
        assert TestEvent in handler.events
        assert TestSecondEvent in handler.events
        assert handler.events[TestEvent] is None
        assert handler.events[TestSecondEvent] is None

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
        assert len(handler.events) == 1
        assert TestEvent in handler.events
        assert isinstance(handler.events[TestEvent], TestEventParameter)

    @app.get("/")
    async def get():
        await test()

    client.get("/")


@pytest.mark.asyncio
async def test_multiple_store_with_parameter(app_with_middleware, client):
    app = app_with_middleware

    async def test():
        await event_handler.store(
            event=TestEvent,
            parameter=TestEventParameter(content="content"),
        )
        await event_handler.store(
            event=TestSecondEvent,
            parameter=TestEventParameter(content="content"),
        )
        handler = event_handler._get_event_handler()
        assert len(handler.events) == 2
        assert TestEvent in handler.events
        assert TestSecondEvent in handler.events
        assert isinstance(handler.events[TestEvent], TestEventParameter)
        assert isinstance(handler.events[TestSecondEvent], TestEventParameter)

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
