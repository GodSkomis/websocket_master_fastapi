from typing import Dict, TYPE_CHECKING

from ws_master.exceptions import NavitagionError
from ws_master.handler import WebSocketHandler

if TYPE_CHECKING:
    from ws_master.schemas import WebSocketRequest


class WebSocketRouter:
    _routes: Dict[str, WebSocketHandler]

    def __init__(self):
        self._routes = dict()
        
    def registrate_handler(self, handler: WebSocketHandler) -> None:
        setup_error_msg = f"Please setup '__route__' attribute of Handler class"
        try:
            if not handler.__route__:
                raise NotImplemented(setup_error_msg)
        except AttributeError:
            raise NotImplemented(setup_error_msg)
        
        if handler.__route__ in self._routes:
            raise ValueError("This route already taken")
        
        self._routes[handler.__route__] = handler
        
    def create_handler(self, route: str) -> WebSocketHandler:
        handler = WebSocketHandler(route)
        self._routes[handler.__route__] = handler
        return handler
    
    def navigate(self, request: "WebSocketRequest"):
        route = request.route
        handler = self._routes.get(route)
        if not handler:
            raise NavitagionError(f'route: "{request.route}" not founded')
        return handler.navigate(request)

    def get_docs(self): # UPDATE!
        return {
            'routes': [
                {
                    'route': route,
                    'events': handler.Event.get_events_docs()
                }
                for route, handler in self._routes.items()
            ] 
        }
