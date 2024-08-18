import logging
import pytest

from fastapi import WebSocket, FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from src.ws_master.event import WebSocketEvent # WebSocketEvent is the main class for handling WebSocket messages
from src.ws_master.event import Response # Response is a class that is filled by AbstractStrategy to determine what and to whom should be sent a result of processing

from src.ws_master.router import WebSocketRouter # WebSocketRouter connects WebSocket requests with WebSocketEvent using keywords in the request. The "route" key links to WebSocketHandler, while the "event" key links to WebSocketEvent, thereby directing the request to the appropriate handler
from src.ws_master.injector import Injector # Injector allows inserting data into the WebSocketEvent interface

from src.ws_master.services import WebSocketService # WebSocketService allows linking various WebSocketClients with a primary key (pk)
from src.ws_master.client import WebSocketClient # WebSocketClient allows you to manage the WebSocket and its connection. It also receives JSON from the WebSocket and attempts to process it


# Setup simple log settings
logging.basicConfig(level=logging.INFO) # Setup simple log settings


class UserSchema(BaseModel): # This schema allows specifying and validating the data that should be contained in the "data" key
    user_id: int


class User: # SQL-model Mock
    id: int
    
    def __init__(self, id: int) -> None:
        self.id = id


Injector.register(User) # Register dependency injection for User type, leave the "provider" parameter empty to pass the data later


websocket_router = WebSocketRouter() # Create WebSocketRouter


echo_handler = websocket_router.create_handler("echo") # Create WebSocketHandler and passing a "route" key


@echo_handler # Use handler as a decorator to link WebSocketEvent with handler
class PingEvent(WebSocketEvent):
    """
        WebSocketRequest example:
            {
                "id": "05.08.2024", # This key is optional, but can help to link request and responseThis key is optional; the request and result have the same value, which can allow them to be linked regardless of the order of requests and responses
                "route": "echo",
                "event": "ping"
            }
            
        WebSocketResponse example:
            {
                "id": "05.08.2024", # The same as the request
                "event": "ping",
                "route": "echo",
                "data": {
                    "data": "Pong" # This is our response
                },
                "error": null # This field can contain errors related to the request(null on success)
            }
    """
    __event_name__ = "ping" # Set a "event" key

    async def handle(self) -> Response | None: # Implement abstract inteface
        response = self.response_builder.create_response({"data": "Pong"}) # Create WebSocketResponse with specefied data
        self.response_builder.add_respondent_strategy(response) # Set WebSocketStrategy through ResponseBuilder


@echo_handler
class UserEvent(WebSocketEvent[UserSchema]): # Set the generic type so that the `data` attribute has the specified type (optional)
    """
        WebSocketRequest example:
            {
                "id": 1234567890,
                "route": "echo",
                "event": "user",
                "data": {
                    "user_id": 11
                }
            }
        
        WebSocketResponse example:
            {
                "id": 1234567890,
                "event": "user",
                "route": "echo",
                "data": {
                    "user": 123, # These data were injected, and the connection URL was "ws://localhost:8000/ws?user_id=123"
                    "user_id_from_request": 11 # These data were obtained from the request
                },
                "error": null
            }
    """
    __event_name__ = "user"
    __schema__ = UserSchema # Set a schema to validate data in "data" key

    async def handle(self, user: User) -> Response | None: # Use a variable of type `User` for dependency injection from the Injector
        response = self.response_builder.create_response({
            "user": user.id,
            "user_id_from_request": self.data.user_id # The validated schema from the "data" key is stored in `self.data`
        })
        self.response_builder.add_respondent_strategy(response)


# Create FastAPi app
app = FastAPI()


# Create a route for WebSocket connections
@app.websocket("/ws")
async def start_chat(websocket: WebSocket, user_id: int = 0): # For injection, we will accept `user_id` from the query parameters during the WebSocket connection
    injector = Injector({User: User(user_id)}) # Create an Injector object and pass the injectable data as needed
    
    # Create a WebSocketClient object and pass all the necessary data to itWebSocketClient, injector is optional
    client = WebSocketClient(
        websocket=websocket,
        pk=user_id,
        router=websocket_router,
        injector=injector
    ) 
    
    await WebSocketService.connect(client) # Through WebSocketService accept the WebSocketClient connection and start handling it

    
@pytest.fixture
def client():
    return TestClient(app)


def test_connection(client: TestClient):
    with client.websocket_connect("/ws") as websocket:
        pass
    

def test_ping(client: TestClient):
    id = 1234567890
    request = \
        {
            "id": id,
            "route": "echo",
            "event": "ping"
        }
    excpected_response =  \
        {
            'id': id,
            'event': 'ping',
            'route': 'echo',
            'data': {
                'data': 'Pong'
            },
            'error': None
        }
        
    with client.websocket_connect("/ws") as websocket:
        websocket.send_json(request)
        assert websocket.receive_json() == excpected_response
       
       
def test_user(client: TestClient):
    id = 12341234
    user_id_in_query_params = 8001
    user_id_in_request = 113
    request = \
        {
            "id": id,
            "route": "echo",
            "event": "user",
            "data": {
                "user_id": user_id_in_request
            }
        }
    excpected_response = \
        {
            "id": id,
            "event": "user",
            "route": "echo",
            "data": {
                "user": user_id_in_query_params,
                "user_id_from_request": user_id_in_request
            },
            "error": None
        }
    
    with client.websocket_connect(f"/ws?user_id={user_id_in_query_params}") as websocket:
        websocket.send_json(request)
        assert websocket.receive_json() == excpected_response
