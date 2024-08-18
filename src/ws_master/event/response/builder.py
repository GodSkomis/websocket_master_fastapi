from typing import TYPE_CHECKING, Dict, Iterable, List

from ws_master.schemas import WebSocketResponse

from .response import Response
from .strategies import ToRespondentClientStrategy, ToServiceClientsStrategy

if TYPE_CHECKING:
    from ws_master.schemas import WebSocketRequest
    from .strategies import AbstractStrategy


class ResponseBuilder:
    _response: Response
    _request: "WebSocketRequest"

    def __init__(self, request: "WebSocketRequest") -> None:
        self._response = Response()
        self._request = request
    
    def add_strategy(self, strategy: "AbstractStrategy") -> None:
        self._response.add_strategy(strategy)

    def add_respondent_strategy(self, response: WebSocketResponse) -> None:
        strategy = ToRespondentClientStrategy(response)
        self.add_strategy(strategy)

    def add_serivce_clients_strategy(self, response: WebSocketResponse, pk: int| str = None, pks: Iterable[int | str] = None) -> None:
        if pk:
            self.add_strategy(ToServiceClientsStrategy(response, pk))
        if not pks:
            return
        for pk in pks:
            self.add_strategy(ToServiceClientsStrategy(response, pk))

    def get_result(self) -> Response:
        return self._response
    
    def create_response(self, data: Dict | List = dict()) -> WebSocketResponse:
        request = self._request.model_copy()
        request.data = data
        response = WebSocketResponse.model_validate(request)
        return response

    def create_error(self, error: str) -> WebSocketResponse:
        response = self._request.model_dump()
        if response.get('data'):
            del response['data']
        response['error'] = error
        response = WebSocketResponse.model_validate(response)
        return response
	
    def create_ok_response(self) -> None:
        response = self._request.model_copy()
        response.data = {"result": "OK"}
        response = WebSocketResponse.model_validate(response)
        return response
        