class InvalidEventTypeException(Exception):
    def __init__(self):
        super().__init__("Event must inherit BaseEvent")


class InvalidParameterTypeException(Exception):
    def __init__(self):
        super().__init__("Parameter must inherit BaseModel")


class EmptyContextException(Exception):
    def __init__(self):
        super().__init__("Event context is empty. check if middleware configured well")
