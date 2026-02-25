import requests  # pyright: ignore[reportMissingModuleSource]
from bs4 import BeautifulSoup  # pyright: ignore[reportMissingImports]


def fetch_web_content(url: str) -> str:
    """
    Fetches the text content of a given URL.
    Use this tool when you need to read the full content of a specific webpage or link.

    Args:
        url: The URL of the webpage to fetch content from.

    Returns:
        The text content of the webpage, or an error message if the fetch fails.
    """

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # 인코딩 설정 (한글 깨짐 방지)
        response.encoding = response.apparent_encoding

        # BeautifulSoup을 사용하여 HTML 파싱 및 텍스트 추출
        soup = BeautifulSoup(response.text, 'html.parser')

        # 불필요한 태그 제거 (스크립트, 스타일, 네비게이션 등)
        for script_or_style in soup(["script", "style", "header", "footer", "nav"]):
            script_or_style.decompose()

        # 텍스트 추출 및 줄바꿈 정리
        text = soup.get_text(separator='\n')
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        clean_text = '\n'.join(lines)

        # 내용이 너무 길 경우 에이전트의 컨텍스트 제한을 고려해 일부 자름 (약 5000자)
        return clean_text[:5000]

    except requests.exceptions.RequestException as e:
        return f"Error fetching the URL: {e}"
    except Exception as e:
        return f"An unexpected error occurred while fetching content: {e}"


if __name__ == "__main__":

    print(fetch_web_content("https://cadabra.tistory.com/164"))
