"""Single-use OAuth state storage for CSRF protection."""
import secrets
import time

_TTL_SECONDS = 600
_states: dict[str, float] = {}

def create_state() -> str:
    now = time.time()
    _states.clear() if len(_states) > 1000 else None
    state = secrets.token_urlsafe(32)
    _states[state] = now
    return state

def consume_state(state: str | None) -> bool:
    if not state:
        return False
    created = _states.pop(state, None)
    return created is not None and time.time() - created <= _TTL_SECONDS
