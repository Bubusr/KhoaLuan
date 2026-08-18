from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseRetriever(ABC):
    @abstractmethod
    def load_corpus(self, corpus_path: str):
        """Tải dữ liệu tri thức nguồn (Corpus)."""
        pass

    @abstractmethod
    def build_index(self):
        """Xây dựng chỉ mục tìm kiếm."""
        pass

    @abstractmethod
    def search(self, query: str, k: int) -> List[Dict[str, Any]]:
        """Tìm kiếm tài liệu liên quan."""
        pass
