from contextvars import ContextVar
from typing import Type, Dict, Union, Optional

from pydantic import BaseModel

from fastapi_event_publisher.base import BaseEvent
from fastapi_event_publisher.exceptions import (
    InvalidEventTypeException,
    InvalidParameterTypeException,
)

_handler_context: ContextVar[Optional, "EventHandler"] = ContextVar(
    "_handler", default=None,
)


class EventHandler:
    def __init__(self):
        self.events: Dict[Type[BaseEvent], Union[BaseModel, None]] = {}

    async def store(
        self, event: Type[BaseEvent], parameter: BaseModel = None,
    ) -> None:
        if not issubclass(event, BaseEvent):
            raise InvalidEventTypeException

        if parameter and not isinstance(parameter, BaseModel):
            raise InvalidParameterTypeException

        self.events[event] = parameter

    async def publish(self) -> None:
        event: Type[BaseEvent]
        for event, parameter in self.events.items():
            await event().run(parameter=parameter)

        self.events.clear()


class EventHandlerMeta(type):
    async def store(
        self, event: Type[BaseEvent], parameter: BaseModel = None,
    ):
        handler = self._get_event_handler()
        await handler.store(event=event, parameter=parameter)

    async def publish(self):
        handler = self._get_event_handler()
        await handler.publish()

    def _get_event_handler(self) -> EventHandler:
        handler = _handler_context.get()
        if not handler:
            raise

        return handler


class EventHandlerDelegator(metaclass=EventHandlerMeta):
    def __init__(self):
        self.token = None

    def __enter__(self):
        self.token = _handler_context.set(EventHandler())
        return type(self)

    def __exit__(self, exc_type, exc_value, traceback):
        _handler_context.reset(self.token)


event_handler: EventHandlerMeta = EventHandlerDelegator