from functools import wraps
from .event_broker import broker


def traced(node_name: str):
    """Emit start and end events around a node call."""

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            broker.emit({"node": node_name, "event": "start"})
            result = fn(*args, **kwargs)
            broker.emit({"node": node_name, "event": "end"})
            return result

        return wrapper

    return decorator
