from typing import Dict, TYPE_CHECKING, Type

from ws_master.schemas import WebSocketRequest
from ws_master.exceptions import NavitagionError

if TYPE_CHECKING:
    from ws_master.event import WebSocketEvent


class WebSocketHandler:
	__route__: str
	__events__: Dict[str, Type["WebSocketEvent"]]
    
	def __init__(self, route: str):
		self.__route__ = route
		self.__events__ = dict()

	def __call__(self, event: Type["WebSocketEvent"]) -> None:
		if not event.__event_name__:
			raise ValueError(f'"__event_name__" is not defined for {event.__class__}')
		event_name =  event.__event_name__
		self.__events__[event_name] = event
		
	def navigate(self, request: "WebSocketRequest") -> "WebSocketEvent":
		if (cls := self.__events__.get(request.event)):
			return cls(request)
		raise NavitagionError(f'event: "{request.event}" does not exists in route: "{request.route}"')
