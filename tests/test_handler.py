from typing import Union, Type

import pytest
from pydantic import BaseModel

from fastapi_event import event_handler, BaseEvent, EventListener
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


class FirstEvent(BaseEvent):
    ORDER = 1

    async def run(self, parameter: Union[Type[BaseModel], None] = None) -> None:
        ...


class SecondEvent(BaseEvent):
    ORDER = 2

    async def run(self, parameter: Union[Type[BaseModel], None] = None) -> None:
        ...


class NoneOrderEvent(BaseEvent):
    async def run(self, parameter: Union[Type[BaseModel], None] = None) -> None:
        ...


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


@pytest.mark.asyncio
async def test_order(app_with_middleware, client):
    app = app_with_middleware

    @EventListener()
    async def test():
        await event_handler.store(event=FirstEvent)
        await event_handler.store(event=SecondEvent)
        maps = await event_handler._get_event_handler()._get_sorted_event_maps()

        assert maps.get(None) == []

        assert len(maps.get(1)) == 1
        assert maps.get(1)[0].event == FirstEvent
        assert maps.get(1)[0].parameter is None

        assert len(maps.get(2)) == 1
        assert maps.get(2)[0].event == SecondEvent
        assert maps.get(2)[0].parameter is None

    @app.get("/")
    async def test_get():
        await test()

    client.get("/")


@pytest.mark.asyncio
async def test_order_if_the_order_of_the_store_is_different(app_with_middleware, client):
    app = app_with_middleware

    @EventListener()
    async def test():
        await event_handler.store(event=SecondEvent)
        await event_handler.store(event=FirstEvent)
        maps = await event_handler._get_event_handler()._get_sorted_event_maps()

        assert maps.get(None) == []

        assert len(maps.get(1)) == 1
        assert maps.get(1)[0].event == FirstEvent
        assert maps.get(1)[0].parameter is None

        assert len(maps.get(2)) == 1
        assert maps.get(2)[0].event == SecondEvent
        assert maps.get(2)[0].parameter is None

    @app.get("/")
    async def test_get():
        await test()

    client.get("/")


@pytest.mark.asyncio
async def test_order_with_none_order(app_with_middleware, client):
    app = app_with_middleware

    @EventListener()
    async def test():
        await event_handler.store(event=FirstEvent)
        await event_handler.store(event=SecondEvent)
        await event_handler.store(event=NoneOrderEvent)
        maps = await event_handler._get_event_handler()._get_sorted_event_maps()

        assert maps.get(None)[0].event == NoneOrderEvent
        assert maps.get(None)[0].parameter is None

        assert len(maps.get(1)) == 1
        assert maps.get(1)[0].event == FirstEvent
        assert maps.get(1)[0].parameter is None

        assert len(maps.get(2)) == 1
        assert maps.get(2)[0].event == SecondEvent
        assert maps.get(2)[0].parameter is None

    @app.get("/")
    async def test_get():
        await test()

    client.get("/")


@pytest.mark.asyncio
async def test_order_with_none_order_if_the_order_of_the_store_is_different(app_with_middleware, client):
    app = app_with_middleware

    @EventListener()
    async def test():
        await event_handler.store(event=SecondEvent)
        await event_handler.store(event=FirstEvent)
        await event_handler.store(event=NoneOrderEvent)
        maps = await event_handler._get_event_handler()._get_sorted_event_maps()

        assert maps.get(None)[0].event == NoneOrderEvent
        assert maps.get(None)[0].parameter is None

        assert len(maps.get(1)) == 1
        assert maps.get(1)[0].event == FirstEvent
        assert maps.get(1)[0].parameter is None

        assert len(maps.get(2)) == 1
        assert maps.get(2)[0].event == SecondEvent
        assert maps.get(2)[0].parameter is None

    @app.get("/")
    async def test_get():
        await test()

    client.get("/")
