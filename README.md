# my_agent

## 프로젝트 개요

**my_agent**는 자율 에이전트 개념을 기반으로 구축된 개인화된 AI 에이전트입니다. Google의 **Gemini** 또는 로컬 **Ollama** 모델을 핵심 두뇌로 사용하여 사용자와 소통하며, 스스로 판단하여 정보를 수집하고 체계적으로 정리합니다.

이 프로젝트는 기존 자율 에이전트의 보안 취약점을 보완하기 위해 **파일 시스템 접근을 엄격하게 제한(Sandboxing)**하며, `docs` 폴더를 에이전트의 "제2의 두뇌(Second Brain)"로 활용합니다.

## 주요 기능

### 1. AI 모델 기반의 지능형 처리

- Google Gemini 또는 로컬 Ollama와 같은 다양한 AI 모델을 사용하여 사용자의 자연어 명령을 이해하고 복잡한 추론을 수행합니다.
- 대화의 맥락을 파악하여 적절한 도구(검색, 파일 저장 등)를 호출합니다.
- **주요 개선 사항**: 이제 `AI_PROVIDER` 환경 변수를 통해 `gemini` 또는 `ollama`를 선택하여 사용할 수 있습니다. 이를 통해 클라우드 기반 모델과 로컬 모델을 유연하게 활용할 수 있습니다.

### 2. 자율적 지식 관리 (Autonomous Knowledge Management)

- **Docs 중심의 기억 저장**: 사용자와의 대화 중 기억해야 할 정보나 요청받은 내용을 `docs` 폴더에 저장합니다.
- **자율적 구조화**: 에이전트는 `docs` 폴더 내에 스스로 하위 폴더를 생성하고, 적절한 마크다운(.md) 파일 이름으로 문서를 작성 및 업데이트합니다.
- **문서 관리 도구**: 에이전트는 `write_doc`, `read_doc`, `list_docs`, `rename_doc`, `move_doc`, `delete_doc`와 같은 기능을 통해 문서를 생성, 읽기, 나열, 이름 변경, 이동, 삭제할 수 있습니다.
- **RAG (Retrieval-Augmented Generation)**: 사용자의 질문에 답하기 위해 인터넷 검색뿐만 아니라, `docs` 폴더에 자신이 기록해 둔 정보를 다시 찾아보고 답변합니다.

### 3. 보안 강화 (Security & Sandboxing)

- **파일 접근 제한**: OpenClaw 유형 에이전트의 보안 취약점을 해소하기 위해, 에이전트의 파일 읽기/쓰기 권한은 오직 `./docs` 디렉토리 내부로만 한정됩니다.
- 시스템의 다른 중요 파일이나 상위 디렉토리 접근은 원천적으로 차단됩니다.

### 4. 멀티 인터페이스 (Multi-Interface)

- **Web UI**: 직관적인 웹 인터페이스를 통해 에이전트와 대화하고, 사이드바의 **문서 탐색기(Document Explorer)**를 통해 실시간으로 생성되는 문서를 확인하거나 내용을 열람할 수 있습니다.
- **Telegram**: 전 세계적으로 널리 쓰이는 텔레그램 메신저를 통해 언제 어디서든 에이전트에게 지시를 내리고 정보를 얻을 수 있습니다.

### 5. 확장 가능한 툴 사용 (Extensible Tool Usage)

my_agent는 다양한 작업을 수행하기 위해 다음과 같은 내장 툴을 활용합니다. 이 툴들은 `src/tools/tool_definitions.py`에서 정의되며, 필요에 따라 쉽게 확장할 수 있습니다.

- **문서 관리 툴 (Document Management Tools)**
  - `write_doc(path, content)`: 새로운 문서를 생성하거나 기존 문서를 업데이트합니다.
  - `read_doc(path)`: 지정된 경로의 문서 내용을 읽습니다.
  - `list_docs(path)`: 지정된 경로 내의 문서 및 디렉토리 목록을 나열합니다.
  - `rename_doc(old_path, new_path)`: 문서 또는 디렉토리의 이름을 변경합니다.
  - `move_doc(source_path, destination_path)`: 문서 또는 디렉토리를 다른 위치로 이동합니다.
  - `delete_doc(path)`: 지정된 경로의 문서 또는 디렉토리를 삭제합니다.
- **정보 검색 툴 (Information Retrieval Tools)**
  - `search_web(query)`: Google 검색을 통해 웹 정보를 검색합니다.
  - `fetch_web_content(url)`: 특정 URL의 웹 페이지 내용을 가져옵니다.
  - `search_arxiv(keyword)`: arXiv에서 학술 논문을 검색합니다.
  - `read_pdf_from_url(url)`: PDF URL에서 텍스트 내용을 추출합니다.
- **유틸리티 툴 (Utility Tools)**
  - `get_current_datetime()`: 현재 날짜와 시간을 반환합니다.

## 기술 스택 (Tech Stack)

- **Language**: Python 3.10+
- **AI Model**: Google Gemini (Flash 2.5 Lite) / Local Ollama (e.g., gpt-oss)
- **Frameworks**: Streamlit (Web UI), python-telegram-bot (Telegram Bot)

## 디렉토리 구조

```text
my_agent/
├── docs/               # [Sandbox] 에이전트가 관리하는 유일한 저장소
│   ├── knowledge/      # (예시) 에이전트가 생성한 주제별 폴더
│   └── logs/           # (예시) 대화 기록 등
├── src/
│   ├── agent_core.py   # Gemini 및 Tool 로직
│   ├── web_ui.py       # 웹 인터페이스 구현체
│   ├── telegram_bot.py # 텔레그램 연동 모듈
│   └── tools/          # 에이전트가 사용하는 모든 외부 도구 정의 및 구현
├── .env                # API 키 설정 파일
└── README.md
```

## 시작하기 (Getting Started)

### 필수 조건 (Prerequisites)

- Python 3.10 이상
- Google Gemini API Key (Gemini 사용 시)
- Ollama 설치 및 모델 다운로드 (Ollama 사용 시)
- (선택) Google Search (Serper) API Key (인터넷 검색용)
- (선택) Telegram Bot Token (텔레그램 연동용)

### 설치 (Installation)

1. 저장소 클론

   ```bash
   git clone https://github.com/your-username/my_agent.git
   cd my_agent
   ```

2. 의존성 패키지 설치

   ```bash
   uv sync
   ```

3. 환경 변수 설정
   `.env` 파일을 생성하고 필요한 키를 입력합니다.

   ```ini
   AI_PROVIDER=gemini # 또는 ollama
   GOOGLE_API_KEY=your_gemini_api_key
   GEMINI_MODEL_NAME=gemini-2.5-flash # Gemini 사용 시

   # Ollama 사용 시
   # OLLAMA_BASE_URL=http://localhost:11434/v1
   # OLLAMA_MODEL_NAME=llama2

   # 인터넷 검색 시
   SEARCH_API_KEY=your_serper_api_key
   # Telegram 사용 시
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   TELEGRAM_AUTHORIZED_USERS=comma_separated_telegram_user_ids # 예: 123456789,987654321
   ```

**TELEGRAM_BOT_TOKEN 획득 방법:**

- 텔레그램에서 `@BotFather`(BotFather)를 검색합니다.
- `/newbot` 명령어를 입력하고 안내에 따라 `봇 이름`과 `사용자명`을 설정합니다.
- 생성이 완료되면 제공되는 `HTTP API token`을 복사하여 `.env` 파일에 붙여넣습니다.

**Telegram User ID 확인 방법:**

- 텔레그램에서 `@userinfobot`(User Info·Get ID·IDbot)을 검색합니다.
- 해당 봇에게 `/start` 명령어를 보내면 자신의 User ID를 알려줍니다.
- 이 ID를 `TELEGRAM_AUTHORIZED_USERS`에 설정합니다. 여러 사용자 ID를 추가하려면 쉼표로 구분합니다 (예: `123456789,987654321`).

## 사용 방법 (Usage)

### 웹 UI 모드

브라우저를 통해 에이전트와 대화하려면 다음 명령어를 실행하세요.

```bash
python my_agent.py run web
```

### Telegram 봇 모드

메신저 연동 서버를 실행하려면 다음 명령어를 실행하세요.

```bash
python my_agent.py run telegram
```

봇이 실행되면, 텔레그램 앱에서 `@<봇사용자이름>` (예: `@my_agent_telegram_bot`)으로 봇을 검색하여 대화를 시작할 수 있습니다.

## 툴 함수 Docstring 작성 가이드 (Tool Function Docstring Guidelines)

`my_agent`는 툴 함수의 Docstring을 분석하여 에이전트의 시스템 명령어(System Instruction)를 자동으로 생성합니다. 따라서 툴 함수를 추가하거나 수정할 때는 다음 가이드라인에 따라 Docstring을 작성해야 에이전트가 툴을 올바르게 이해하고 활용할 수 있습니다.

- **첫 줄 (Summary):** 툴의 목적과 언제 사용해야 하는지 간결하게 설명합니다. 이 부분이 에이전트의 주요 지침으로 사용됩니다.
- **상세 설명 (Details):** 첫 줄 이후에 툴의 기능, 인자, 반환 값 등에 대한 자세한 설명을 추가할 수 있습니다. 에이전트가 툴을 더 잘 이해하고 정확하게 사용할 수 있도록 돕습니다.
- **예시 (Examples - Optional):** 필요한 경우 툴 사용 예시를 추가하여 에이전트의 이해를 돕습니다.

**예시:**

```python
def example_tool(arg1: str, arg2: int) -> str:
    """
    이 툴은 arg1과 arg2를 사용하여 어떤 작업을 수행합니다.
    사용자가 X를 요청할 때 이 툴을 사용하세요.

    Args:
        arg1: 첫 번째 인자에 대한 설명입니다.
        arg2: 두 번째 인자에 대한 설명입니다.

    Returns:
        작업 결과에 대한 설명입니다.
    """
    # ... 툴 구현 ...
    pass
```

## 라이선스

MIT License
