# fastapi-event
[![license]](/LICENSE)
[![pypi]](https://pypi.org/project/fastapi-event/)
[![pyversions]](http://pypi.python.org/pypi/fastapi-event)

---

fastapi-event is event dispatcher for FastAPI framework.

## Installation

```python
pip3 install fastapi-event
```

## Usage

### Make Event

```python
from fastapi_event import BaseEvent


class TestEvent(BaseEvent):
    async def run(self, parameter=None):
        ...
```

Inherit `BaseEvent` and override `run()` method.

```python
from fastapi_event import BaseEvent


class FirstEvent(BaseEvent):
    ORDER = 1  # HERE(Optional)
    
    async def run(self, parameter=None):
        ...


class SecondEvent(BaseEvent):
    ORDER = 2  # HERE(Optional)
    
    async def run(self, parameter=None):
        ...
```

If you want to determine the order between events, specify `ORDER` in your event. 

Then, regardless of the order in which the events are stored, they will be executed in the order specified in `ORDER` variable.

However, `ORDER` does not work when `run_at_once=True`.

### Parameter(optional)

```python
from pydantic import BaseModel


class TestEventParameter(BaseModel):
    id: str
    pw: str
```

In case of need parameter, you have to inherit `BaseModel` and set fields.

### Middleware

```python
from fastapi import FastAPI
from fastapi_event import EventHandlerMiddleware

app = FastAPI()
app.add_middleware(EventHandlerMiddleware)
```

### EventListener

```python
from fastapi_event import EventListener


@EventListener()
async def test():
    ...
```

Set `@EventListener()` decorator on the function that emits the event.

```python
@EventListener(run_at_once=False)
```

If you pass `run_at_once=False`, it will execute in the order in which `store()` is called. (or according to the `ORDER` variable defined in the event)

Otherwise, it will execute through `asyncio.gather()` to run at once.

### Store event

```python
from fastapi_event import EventListener, event_handler


@EventListener()
async def test():
    await event_handler.store(
        event=TestEvent,
        parameter=TestParameter(id="hide", pw="hide"),  # Optional
    )
```

Store your event to handler via `store()` method. (parameter is optional)

An event will be emitted after the function has finished executing.

[license]: https://img.shields.io/badge/License-Apache%202.0-blue.svg
[pypi]: https://img.shields.io/pypi/v/fastapi-event
[pyversions]: https://img.shields.io/pypi/pyversions/fastapi-event