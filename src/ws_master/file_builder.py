import argparse
import os


class FileBuilder:
    app_name: str
    app_folder_path: str
    
    def __init__(self, app_name: str) -> None:
        if not app_name:
            raise ValueError(f"Wrong app_name: '{app_name}'")
        self.app_name = app_name
        current_directory = os.getcwd()
        self.app_folder_path = os.path.join(current_directory, self.app_name)
        
    def gen_handler(self):
        file_content = \
f"""from ws_master.event.response import Response
from ws_master.event import WebSocketEvent
from pydantic import BaseModel

from .schemas import request_schemas, response_schemas

from ... import ... as websocket_router #import your WebSocketRouter there


{self.app_name.upper()}_HANDLER = websocket_router.create_handler("{self.app_name}")


@{self.app_name.upper()}_HANDLER
class {self.app_name.capitalize()}Event(WebSocketEvent[...]):
    __event_name__: str = 
    __schema__: BaseModel = 
    
    async def handle(self) -> Response | None:
        pass
"""
        with open(os.path.join(self.app_folder_path, "handler.py"), 'w+') as file:
            file.write(file_content)

    def gen_schemas(self):
        file_content = """from pydantic import Basemodel
        """
        schemas_folder_path = os.path.join(self.app_folder_path, "schemas")
        os.mkdir(schemas_folder_path)
        with open(os.path.join(schemas_folder_path, "request_schrmas.py"), 'w+') as file:
            file.write(file_content)
        with open(os.path.join(schemas_folder_path, "response_schemas.py"), 'w+') as file:
            file.write(file_content)
    
    def gen_models(self):
        file_content = \
f"""from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from ... import Base #Import Base SqlAlchemy there

class {self.app_name.capitalize()}(Base):
    __tablename__ = "{self.app_name}"
"""
        with open(os.path.join(self.app_folder_path, "models.py"), 'w+') as file:
            file.write(file_content)
        

    def build(self):
        current_directory = os.getcwd()
        app_folder_path = os.path.join(current_directory, self.app_name)
        os.mkdir(app_folder_path)
        self.gen_handler()
        self.gen_schemas()
    
    
def main():
    parser = argparse.ArgumentParser(description="WS Master app builder")
    parser.add_argument('--name', type=str, help='App name', required=True)
    parser.add_argument(
        '--sql',
        action='store_true',
        help='Create sql model'
    )
    args = parser.parse_args()
    app_name = args.name
    builder = FileBuilder(app_name)
    builder.build()
    if args.sql:
        builder.gen_models()


if __name__ == "__main__":
    main()
