from typing import Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
	from ws_master.client import WebSocketClient
	from ws_master.schemas import WebSocketResponse


class WebSocketService:
	_clients: Dict[int | str, List["WebSocketClient"]] = dict()

	@classmethod
	async def connect(cls, client: "WebSocketClient") -> None:
		if client.pk not in cls._clients:
			cls._clients[client.pk] = list()
		cls._clients[client.pk].append(client)
		await client.connect()
		cls._clients[client.pk].remove(client)

	@classmethod
	async def send(cls, response: "WebSocketResponse", pk: int | str) -> None:
		if pk not in cls._clients:
			return
		clients = cls._clients.get(pk)
		for client in clients:
			await client.websocket.send_json(response.model_dump())
