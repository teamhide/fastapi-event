from pydantic import BaseModel

from fastapi_event import BaseEvent


class TestEvent(BaseEvent):
    __test__ = False

    async def run(self, parameter=None) -> None:
        pass


class TestSecondEvent(BaseEvent):
    __test__ = False

    async def run(self, parameter=None) -> None:
        pass


class TestEventDoNotHaveParameter(BaseEvent):
    __test__ = False

    async def run(self):
        pass


class TestEventParameter(BaseModel):
    __test__ = False

    content: str


class TestEventParameterNotNone(BaseEvent):
    __test__ = False

    async def run(self, parameter):
        pass
