from __future__ import annotations

import logging
from typing import Callable

log = logging.getLogger(__name__)

CommandHandler = Callable[[dict], None]


class CommandDispatcher:

    def __init__(self) -> None:
        self._handlers: dict[str, CommandHandler] = {}

    def register(self, action: str, handler: CommandHandler) -> None:
        self._handlers[action] = handler

    def dispatch(self, payload: dict) -> None:
        action = payload.get("action")
        if not action:
            log.warning("[Dispatcher] Payload missing 'action': %s", payload)
            return
        handler = self._handlers.get(action)
        if handler is None:
            log.warning("[Dispatcher] Unknown action '%s' – registered: %s",
                        action, list(self._handlers))
            return
        try:
            handler(payload)
        except Exception as exc:
            log.exception("[Dispatcher] Handler for '%s' raised: %s", action, exc)
