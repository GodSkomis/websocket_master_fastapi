from fastapi import WebSocket
from ws_master.schemas import WebSocketResponse
from ws_master.services import WebSocketService
from .abstracts import AbstractStrategy


class ToRespondentClientStrategy(AbstractStrategy):
    _response: WebSocketResponse
    
    def __init__(self, response: WebSocketResponse) -> None:
        self._response = response
        
    async def __call__(self, websocket: WebSocket) -> None:
        await websocket.send_json(self._response.model_dump())
    
    
class ToServiceClientsStrategy(AbstractStrategy):
    _response: WebSocketResponse
    _pk: int | str
    
    def __init__(self, response: WebSocketResponse, pk: int | str) -> None:
        self._response = response
        self._pk = pk
        
    async def __call__(self, websocket: WebSocket) -> None:
        await WebSocketService.send(self._response, self._pk)
