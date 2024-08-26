from typing import Dict,TYPE_CHECKING, Optional
from abc import ABC, abstractmethod

from fastapi import WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
from pydantic import ValidationError

from ws_master.schemas import WebSocketRequest
from ws_master.exceptions import EventError, CriticalEventError


if TYPE_CHECKING:
    from ws_master.router import WebSocketRouter
    from ws_master.injector import Injector


class AbstractWebSocketClient(ABC):
    @abstractmethod
    async def handle(self, request: WebSocketRequest) -> None:
        pass
    

class WebSocketClient(AbstractWebSocketClient):
    _websocket: WebSocket
    _pk: int | str
    _router: "WebSocketRouter"
    _injector: Optional["Injector"] = None
    _is_closed: bool

    @property
    def is_closed(self):
        return self._is_closed

    @property
    def websocket(self):
        return self._websocket
    
    @property
    def pk(self):
        return self._pk

    def __init__(self, websocket: WebSocket, pk: int| str, router: "WebSocketRouter", injector: "Injector" = None):
        self._websocket = websocket
        self._pk = pk
        self._router = router
        self._injector = injector

    async def connect(self) -> None:
        await self._websocket.accept()
        self._is_closed = False
        try:
            while not self._is_closed:
                request_data: Dict = await self._websocket.receive_json()
                try:
                    request = await self.prepare(request_data)
                    await self.handle(request)
                except ValidationError | EventError  as ex:
                    await self._websocket.send_json(ex)
                    continue
                except CriticalEventError as ex:
                    await self._websocket.send_json(ex)
                    break
            await self.disconnect()
        except WebSocketDisconnect:
            await self.disconnect()

    async def disconnect(self) -> None:
        if self._websocket.client_state == WebSocketState.CONNECTED:
            await self._websocket.close()
            self._is_closed = True

    async def handle(self, request: WebSocketRequest) -> None:
        event = self._router.navigate(request)
        if not event:
            return      
        event_coro = self._injector.inject_async(event.handle) if self._injector else event.handle
        response = await event_coro()
        if not response:
            response = event.response_builder.get_result()
        await response.execute(self._websocket)

    async def prepare(self, request_data: Dict) -> WebSocketRequest:
        return WebSocketRequest(**request_data)
