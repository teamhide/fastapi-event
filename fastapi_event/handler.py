import asyncio
import inspect
from contextvars import ContextVar
from pydantic import BaseModel
from typing import Type, Dict, Union, Optional, List

from fastapi_event.base import BaseEvent
from fastapi_event.exceptions import (
    InvalidEventTypeException,
    InvalidParameterTypeException,
    EmptyContextException,
    RequiredParameterException,
    ParameterCountException,
    InvalidOrderTypeException,
)

_handler_context: ContextVar[Optional, "EventHandler"] = ContextVar(
    "_handler_context",
    default=None,
)


class EventAndParameter(BaseModel):
    event: Type[BaseEvent]
    parameter: Optional[BaseModel] = None


class EventHandlerValidator:
    EVENT_PARAMETER_COUNT = 2

    async def validate(
        self, event: Type[BaseEvent], parameter: BaseModel = None,
    ) -> None:
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

    async def store(self, event: Type[BaseEvent], parameter: BaseModel = None) -> None:
        await self.validator.validate(event=event, parameter=parameter)
        self.events[event] = parameter

    async def _publish(self, run_at_once: bool = True) -> None:
        if run_at_once is True:
            await self._run_at_once()
        else:
            await self._run_sequentially()

        self.events.clear()

    async def _run_at_once(self) -> None:
        futures = []
        event: Type[BaseEvent]
        for event, parameter in self.events.items():
            task = asyncio.create_task(event().run(parameter=parameter))
            futures.append(task)

        await asyncio.gather(*futures)

    async def _run_sequentially(self) -> None:
        event_maps = await self._get_sorted_event_maps()
        keys = await self._get_sorted_keys(maps=event_maps)

        for key in keys:
            info = event_maps.get(key)
            for each in info:
                await each.event().run(parameter=each.parameter)

    async def _get_sorted_keys(
        self, maps: Dict[Optional[int], List[EventAndParameter]]
    ) -> List[Optional[int]]:
        keys: List[Optional[int]] = sorted(
            [key for key in maps.keys() if key is not None]
        )
        if maps.get(None):
            keys.append(None)

        return keys

    async def _get_sorted_event_maps(
        self,
    ) -> Dict[Optional[int], List[EventAndParameter]]:
        """
        event_maps = {
            1: [EventAndParameter],
            2: [EventAndParameter],
            None: [EventAndParameter],
        }
        """
        event_maps: Dict[Optional[int], List[EventAndParameter]] = {None: []}

        for event, parameter in self.events.items():
            if event.ORDER and not isinstance(event.ORDER, int):
                raise InvalidOrderTypeException

            info = EventAndParameter(event=event, parameter=parameter)
            if not event.ORDER:
                event_maps.get(None).append(info)
            elif event.ORDER not in event_maps:
                event_maps[event.ORDER] = [info]
            else:
                event_maps.get(event.ORDER).append(info)

        return event_maps


class EventHandlerMeta(type):
    async def store(self, event: Type[BaseEvent], parameter: BaseModel = None) -> None:
        handler = self._get_event_handler()
        await handler.store(event=event, parameter=parameter)

    async def _publish(self, run_at_once: bool = True) -> None:
        handler = self._get_event_handler()
        await handler._publish(run_at_once=run_at_once)

    def _get_event_handler(self) -> EventHandler:
        try:
            return _handler_context.get()
        except LookupError:
            raise EmptyContextException


class EventHandlerDelegator(metaclass=EventHandlerMeta):
    validator = EventHandlerValidator()

    def __init__(self):
        self.token = None

    def __enter__(self):
        self.token = _handler_context.set(EventHandler(validator=self.validator))
        return type(self)

    def __exit__(self, exc_type, exc_value, traceback):
        _handler_context.reset(self.token)


event_handler: Type[EventHandlerDelegator] = EventHandlerDelegator
