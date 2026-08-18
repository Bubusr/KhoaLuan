from abc import ABC, abstractmethod
from src.models import StructuredQuery

class BaseParser(ABC):
    @abstractmethod
    def parse(self, query: str) -> StructuredQuery:
        """Trích xuất bối cảnh lâm sàng y khoa từ câu hỏi thô."""
        pass
