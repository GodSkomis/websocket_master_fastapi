from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional, Type

from .response import ResponseBuilder

if TYPE_CHECKING:
    from ws_master.schemas import WebSocketRequest
    from pydantic import BaseModel
    from .response import Response


class WebSocketEvent[T: BaseModel](ABC):
    __event_name__: str = None
    __schema__: Type[T] = None
    _request: "WebSocketRequest"
    response_builder: ResponseBuilder
    data: T = None
    
    @abstractmethod
    async def handle(self, *args, **kwargs) -> Optional["Response"]:
        pass
    
    def __init__(self, request: "WebSocketRequest"):
        if self.__schema__:
            self.data = self.__schema__(**request.data)
        self._request = request
        self.response_builder = ResponseBuilder(request)
    