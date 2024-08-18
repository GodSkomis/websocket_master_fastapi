from typing import List, TYPE_CHECKING


if TYPE_CHECKING:
    from fastapi import WebSocket
    from .strategies.abstracts import AbstractStrategy


class Response:
    _strategies: List["AbstractStrategy"]

    def __init__(self) -> None:
        self._strategies = list()

    async def execute(self, websocket: "WebSocket") -> None:
        for strategy in self._strategies:
            await strategy(websocket)

    def add_strategy(self, strategy: "AbstractStrategy") -> None:
        self._strategies.append(strategy)
        