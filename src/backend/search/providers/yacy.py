import urllib3
import urllib.parse
import requests
from backend.schemas import SearchResponse, SearchResult
from backend.search.providers.base import SearchProvider


class YacySearchProvider(SearchProvider):
    def __init__(self, yacy_host, source_count):
        print("im in Yacy")
        self.yacy_host = yacy_host
        self.source_count = source_count
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                

    async def search(self, query: str) -> SearchResponse:
        try:
            self.request_query = self.yacy_host+ "/yacysearch.json?query="+ query +"&count="+str(self.source_count)
            print("my request query", self.request_query)
            response = requests.get(self.request_query, verify=False)
            searchresult = response.json()
            if searchresult is None:
                raise ValueError("No search result response from Yacy")
            data = response.json()
            results = []
            for item in data["channels"][0]["items"]:
                result = SearchResult(
                            title=item["title"],
                                url=item["link"],
                                content=item["description"]
                                )
                results.append(result)

            #    Create and return the SearchResponse with the populated results list
            search_response = SearchResponse(results=results)

            # Debugging: Print results for confirmation
            print(f"Result size is {len(results)}")
            for res in results:
                print(res)

            return search_response

        except requests.exceptions.RequestException as e:
            print("An error occurred in yacy wihtout requests:", e)

    async def search_keyword(self, query_keyword: str) -> SearchResponse:
        try:
            key_word_query = " ".join(query_keyword)
            key_word_query = key_word_query.strip('"')
            params = {
                 "q": key_word_query	,  # This ensures no quotes are explicitly added
                "defType": "edismax",
                "q.op": "OR",
                "start": 0,
                "rows": self.source_count,
                "core": "collection1",
                "wt": "json",
                }

            # Use urlencode to safely encode the entire query
            encoded_params = urllib.parse.urlencode(params)

            # Construct the full URL
            self.request_query = f"http://192.168.178.44:8090/solr/select?{encoded_params}"
            print("my request query", self.request_query)
            response = requests.get(self.request_query, verify=False)
            searchresult = response.json()
            if searchresult is None:
                raise ValueError("No search result response from Yacy with keyword")
            data = response.json()
            results = []
            
            for doc in data["response"]["docs"]:
                result = SearchResult(title=doc.get("title", ["N/A"])[0],  # Get the first title if it's a list
                                        url=doc.get("sku", "N/A"),
                                        content=doc.get("text_t", "N/A"))
                results.append(result)
            # Create and return the SearchResponse with the populated results list
            search_response = SearchResponse(results=results)

            
            # Debugging: Print results for confirmation
            print(f"Result size is {len(results)}")
            return search_response

        except requests.exceptions.RequestException as e:
            print("An error occurred in yacy keyword requests:", e)


