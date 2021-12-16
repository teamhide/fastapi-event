import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_event import EventHandlerMiddleware


@pytest.fixture
def app():
    yield FastAPI()


@pytest.fixture
def app_with_middleware(app):
    app: FastAPI
    app.add_middleware(EventHandlerMiddleware)
    yield app


@pytest.fixture
def client(app):
    with TestClient(app) as client:
        yield client
