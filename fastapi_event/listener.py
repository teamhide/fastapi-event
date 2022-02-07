from fastapi_event.handler import event_handler


class EventListener:
    def __init__(self, run_at_once: bool = True):
        self.run_at_once = run_at_once

    def __call__(self, func):
        async def _inner(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
            except Exception as e:
                raise e from None

            await event_handler.publish(run_at_once=self.run_at_once)
            return result

        return _inner
