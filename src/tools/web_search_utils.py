import json
import os
import requests  # pyright: ignore[reportMissingModuleSource]
from ddgs import DDGS  # DuckDuckGo 검색 라이브러리 추가


def search_web_serper(query: str, num_results: int = 20) -> str:
    """
    Performs a web search using the Serper API and returns a formatted string of results.
    Use this tool when the user asks for general information, current events, or needs to search the web.

    Args:
        query: The search query (e.g., "latest news on AI").
        num_results: The maximum number of search results to return.

    Returns:
        A formatted string containing the title, snippet, and link for each search result,
        or an error message if the search fails.
    """

    api_key = os.getenv("SEARCH_API_KEY")
    if not api_key:
        return "Error: SEARCH_API_KEY not found in environment variables. Please set it in a .env file."

    url = "https://google.serper.dev/search"
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    payload = json.dumps({"q": query, "num": num_results})

    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        search_results = response.json()

        if search_results.get("organic"):
            formatted_results = []
            for result in search_results["organic"]:
                title = result.get("title")
                snippet = result.get("snippet")
                link = result.get("link")
                if title and snippet and link:
                    formatted_results.append(
                        f"Title: {title}\nSnippet: {snippet}\nLink: {link}\n")
            return "\n---\n".join(formatted_results)
        else:
            return "No organic search results found."
    except requests.exceptions.RequestException as e:
        return f"Error performing web search: {e}"
    except Exception as e:
        return f"An unexpected error occurred during web search: {e}"


def search_web_ddgs(query: str, num_results: int = 5) -> str:
    """
    Performs a web search using DuckDuckGo (Free, No API Key required).

    Args:
        query: The search query.
        num_results: The maximum number of search results to return.

    Returns:
        A formatted string containing title, snippet, and link.
    """

    try:
        formatted_results = []

        # DDGS 컨텍스트 매니저를 사용하여 검색 수행
        with DDGS() as ddgs:
            # region="wt-wt"는 전세계를 의미하며, 한국어 결과 위주라면 "kr-kr" 사용 가능
            results = ddgs.text(query, max_results=num_results, region="wt-wt")

            for r in results:
                title = r.get("title")
                snippet = r.get("body")  # DDG는 snippet 대신 body 키를 사용함
                link = r.get("href")    # DDG는 link 대신 href 키를 사용함

                if title and snippet and link:
                    formatted_results.append(
                        f"Title: {title}\nSnippet: {snippet}\nLink: {link}\n"
                    )

        if not formatted_results:
            return "No search results found on DuckDuckGo."

        return "\n---\n".join(formatted_results)

    except Exception as e:
        return f"An error occurred during DuckDuckGo search: {e}"


def search_web(query: str, num_results: int = 20) -> str:
    """
    Performs a web search.
    Use this tool when the user asks for general information, current events, or needs to search the web.

    Args:
        query: The search query.
        num_results: The maximum number of search results to return.

    Returns:
        A formatted string containing title, snippet, and link.
    """

    return search_web_ddgs(query, num_results)


if __name__ == "__main__":

    # Example usage (requires SEARCH_API_KEY in .env)
    # from dotenv import load_dotenv
    # load_dotenv()
    # print(search_web_serper("what is the weather like in Seoul"))
    print(search_web_ddg("what is the weather like in Seoul"))

    pass
