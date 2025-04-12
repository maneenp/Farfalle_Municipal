from abc import ABC, abstractmethod

from backend.schemas import SearchResponse


class SearchProvider(ABC):
    @abstractmethod
    async def search(self, query: str) -> SearchResponse:
        pass

    @abstractmethod
    async def search_keyword(self, query_keyword: str) -> SearchResponse:
        pass
