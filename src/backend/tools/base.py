from abc import ABC, abstractmethod
from typing import Any, Dict, Type
from pydantic import BaseModel


class BaseTool(ABC):

    name: str
    description: str
    args_schema: Type[BaseModel]

    @abstractmethod
    def _run(self, **kwargs) -> Any:
        pass

    def to_metadata(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.args_schema.model_json_schema()
        }