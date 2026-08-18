from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple
from src.models import StructuredQuery

class BaseGenerator(ABC):
    @abstractmethod
    def generate_answer(self, query: str, chunks: List[Dict[str, Any]], structured_query: StructuredQuery) -> Tuple[str, str]:
        """Sinh câu trả lời y tế và trả về quyết định y khoa (Answer, Abstain, Escalate)."""
        pass
