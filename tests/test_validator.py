import pytest

from fastapi_event.exceptions import (
    InvalidEventTypeException,
    InvalidParameterTypeException,
    ParameterCountException,
    RequiredParameterException,
)
from fastapi_event.handler import EventHandlerValidator
from tests.events import (
    TestEvent,
    TestEventParameter,
    TestEventDoNotHaveParameter,
    TestEventParameterNotNone,
)


@pytest.mark.asyncio
async def test_validate_with_invalid_event_type_exception():
    class Event:
        pass

    with pytest.raises(InvalidEventTypeException):
        await EventHandlerValidator().validate(
            event=Event, parameter=TestEventParameter(content="content"),
        )


@pytest.mark.asyncio
async def test_validate_with_invalid_parameter_type_exception():
    class Parameter:
        pass

    with pytest.raises(InvalidParameterTypeException):
        await EventHandlerValidator().validate(
            event=TestEvent, parameter=Parameter(),
        )


@pytest.mark.asyncio
async def test_validate_with_parameter_count_exception():
    with pytest.raises(ParameterCountException):
        await EventHandlerValidator().validate(
            event=TestEventDoNotHaveParameter,
            parameter=TestEventParameter(content="content"),
        )


@pytest.mark.asyncio
async def test_validate_with_required_parameter_exception():
    with pytest.raises(RequiredParameterException):
        await EventHandlerValidator().validate(
            event=TestEventParameterNotNone,
        )


@pytest.mark.asyncio
async def test_validate():
    result = await EventHandlerValidator().validate(
        event=TestEvent,
        parameter=TestEventParameter(content="content")
    )
    assert result is None
