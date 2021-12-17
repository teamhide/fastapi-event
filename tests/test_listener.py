import pytest

from fastapi_event import EventListener, event_handler, BaseEvent
from tests.events import TestEvent, TestEventParameter

GLOBAL_VAR = 0


@pytest.mark.asyncio
async def test_listener_is_publish_works_well(app_with_middleware, client):
    app = app_with_middleware

    @EventListener()
    async def test():
        await event_handler.store(
            event=TestEvent,
            parameter=TestEventParameter(content="content"),
        )

    @app.get("/")
    async def test_get():
        assert event_handler._get_event_handler().events == {}
        await test()
        assert event_handler._get_event_handler().events == {}

    client.get("/")


@pytest.mark.asyncio
async def test_listener_is_event_emitted_well(app_with_middleware, client):
    app = app_with_middleware

    class TestEventThatChangeGlobalVar(BaseEvent):
        async def run(self, parameter=None) -> None:
            global GLOBAL_VAR
            GLOBAL_VAR = 1

    @EventListener()
    async def test():
        await event_handler.store(
            event=TestEventThatChangeGlobalVar,
        )

    @app.get("/")
    async def test_get():
        global GLOBAL_VAR
        assert event_handler._get_event_handler().events == {}
        await test()
        assert event_handler._get_event_handler().events == {}
        assert GLOBAL_VAR == 1

    client.get("/")


@pytest.mark.asyncio
async def test_listener_run_at_once(app_with_middleware, client):
    app = app_with_middleware

    @EventListener(run_at_once=True)
    async def test():
        await event_handler.store(
            event=TestEvent,
            parameter=TestEventParameter(content="content"),
        )

    @app.get("/")
    async def test_get():
        assert event_handler._get_event_handler().events == {}
        await test()
        assert event_handler._get_event_handler().events == {}

    client.get("/")
