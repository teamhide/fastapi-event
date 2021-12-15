from fastapi_event_publisher.handler import event_handler


class EventListener:
    def __call__(self, func):
        async def _inner(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
            except Exception as e:
                raise e from None

            await event_handler.publish()
            return result

        return _inner
