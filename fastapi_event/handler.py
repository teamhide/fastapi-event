import inspect
from contextvars import ContextVar
from typing import Type, Dict, Union, Optional, NoReturn

from pydantic import BaseModel

from fastapi_event.base import BaseEvent
from fastapi_event.exceptions import (
    InvalidEventTypeException,
    InvalidParameterTypeException,
    EmptyContextException,
    RequiredParameterException,
    ParameterCountException,
)

_handler_context: ContextVar[Optional, "EventHandler"] = ContextVar(
    "_handler_context", default=None,
)


class EventHandlerValidator:
    EVENT_PARAMETER_COUNT = 2

    async def validate(
        self, event: Type[BaseEvent], parameter: BaseModel = None,
    ) -> Optional[NoReturn]:
        if not issubclass(event, BaseEvent):
            raise InvalidEventTypeException

        if parameter and not isinstance(parameter, BaseModel):
            raise InvalidParameterTypeException

        signature = inspect.signature(event.run)
        func_parameters = signature.parameters
        if len(func_parameters) != self.EVENT_PARAMETER_COUNT:
            raise ParameterCountException

        base_parameter = func_parameters.get("parameter")
        if base_parameter.default is not None and not parameter:
            raise RequiredParameterException(
                cls_name=base_parameter.__class__.__name__,
            )


class EventHandler:
    def __init__(self, validator: EventHandlerValidator):
        self.events: Dict[Type[BaseEvent], Union[BaseModel, None]] = {}
        self.validator = validator

    async def store(
        self, event: Type[BaseEvent], parameter: BaseModel = None,
    ) -> None:
        await self.validator.validate(event=event, parameter=parameter)
        self.events[event] = parameter

    async def publish(self) -> None:
        event: Type[BaseEvent]
        for event, parameter in self.events.items():
            await event().run(parameter=parameter)

        self.events.clear()


class EventHandlerMeta(type):
    async def store(
        self, event: Type[BaseEvent], parameter: BaseModel = None,
    ) -> None:
        handler = self._get_event_handler()
        await handler.store(event=event, parameter=parameter)

    async def publish(self) -> None:
        handler = self._get_event_handler()
        await handler.publish()

    def _get_event_handler(self) -> Union[EventHandler, NoReturn]:
        try:
            return _handler_context.get()
        except LookupError:
            raise EmptyContextException


class EventHandlerDelegator(metaclass=EventHandlerMeta):
    def __init__(self):
        self.token = None

    def __enter__(self):
        validator = EventHandlerValidator()
        self.token = _handler_context.set(EventHandler(validator=validator))
        return type(self)

    def __exit__(self, exc_type, exc_value, traceback):
        _handler_context.reset(self.token)


event_handler: Type[EventHandlerDelegator] = EventHandlerDelegator
