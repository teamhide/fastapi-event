# fastapi-event
[![license]](/LICENSE)
[![pypi]](https://pypi.org/project/fastapi-event/)
[![pyversions]](http://pypi.python.org/pypi/fastapi-event)
![badge](https://action-badges.now.sh/teamhide/fastapi-event)
[![Downloads](https://pepy.tech/badge/fastapi-event)](https://pepy.tech/project/fastapi-event)

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

You have to inherit `BaseEvent` and override `run()` method.

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