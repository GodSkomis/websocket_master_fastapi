from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class WebSocketRequest(BaseModel):
	id: Optional[int | str] = None
	event: str
	route: str
	data: Optional[Dict | List] = dict()

	model_config = ConfigDict(from_attributes=True)


class WebSocketResponse(WebSocketRequest):
	error: Optional[str] = None
 