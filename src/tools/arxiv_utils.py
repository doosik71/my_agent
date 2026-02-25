import arxiv  # pyright: ignore[reportMissingImports]
from typing import List, Dict


def search_arxiv(query: str, max_results: int = 5) -> List[Dict]:
    """
    Searches arXiv for academic papers matching the query.
    Use this tool when the user asks to find academic papers or research materials.

    Args:
        query: The search query (e.g., "large language models").
        max_results: The maximum number of search results to return.

    Returns:
        A list of dictionaries, where each dictionary represents a paper with:
        - 'title': The title of the paper.
        - 'authors': A comma-separated string of author names.
        - 'summary': The abstract of the paper.
        - 'url': The URL to the arXiv page.
        - 'pdf_url': The URL to the PDF document.
    """
    try:
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance,
            sort_order=arxiv.SortOrder.Descending
        )

        results = []
        for result in search.results():
            authors = ", ".join([author.name for author in result.authors])
            results.append({
                "title": result.title,
                "authors": authors,
                "summary": result.summary,
                "url": result.entry_id,
                "pdf_url": result.pdf_url
            })
        return results
    except Exception as e:
        return [{"error": f"Error searching arXiv: {e}"}]


if __name__ == "__main__":
    # Example usage:
    # results = search_arxiv("reinforcement learning", max_results=2)
    # for res in results:
    #     print(f"Title: {res['title']}")
    #     print(f"Authors: {res['authors']}")
    #     print(f"URL: {res['url']}")
    #     print(f"PDF URL: {res['pdf_url']}")
    #     print("-" * 20)
    pass
