from abc import ABC, abstractmethod
from typing import List, Dict, Any
from src.models import StructuredQuery

class BaseReranker(ABC):
    @abstractmethod
    def rerank(self, candidates: List[Dict[str, Any]], structured_query: StructuredQuery) -> List[Dict[str, Any]]:
        """Sắp xếp lại thứ tự ưu tiên của tài liệu."""
        pass
