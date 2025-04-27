from abc import ABC, abstractmethod

from backend.schemas import SearchResponse


class SearchProvider(ABC):
    @abstractmethod
    async def search(self, query: str, solr_query_type: bool) -> SearchResponse:
        pass

    @abstractmethod
    async def search_keyword(self, query_keyword: str, solr_query_type: bool) -> SearchResponse:
        pass
