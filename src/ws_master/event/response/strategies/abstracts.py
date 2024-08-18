from abc import ABC, abstractmethod

from fastapi import WebSocket


class AbstractStrategy(ABC):

    def __init__(self, *args, **kwargs) -> None:
        pass   

    @abstractmethod
    async def __call__(self, websocket: WebSocket) -> None:
        pass
