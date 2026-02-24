# my_agent

## 프로젝트 개요

**my_agent**는 OpenClaw(Open Interpreter 계열)의 자율 에이전트 개념을 기반으로 구축된 개인화된 AI 에이전트입니다. Google의 **Gemini** 모델을 핵심 두뇌로 사용하여 사용자와 소통하며, 스스로 판단하여 정보를 수집하고 체계적으로 정리합니다.

이 프로젝트는 기존 자율 에이전트의 보안 취약점을 보완하기 위해 **파일 시스템 접근을 엄격하게 제한(Sandboxing)**하며, `docs` 폴더를 에이전트의 "제2의 두뇌(Second Brain)"로 활용합니다.

## 주요 기능

### 1. Gemini 기반의 지능형 처리

- Google Gemini 모델을 사용하여 사용자의 자연어 명령을 이해하고 복잡한 추론을 수행합니다.
- 대화의 맥락을 파악하여 적절한 도구(검색, 파일 저장 등)를 호출합니다.

### 2. 자율적 지식 관리 (Autonomous Knowledge Management)

- **Docs 중심의 기억 저장**: 사용자와의 대화 중 기억해야 할 정보나 요청받은 내용을 `docs` 폴더에 저장합니다.
- **자율적 구조화**: 에이전트는 `docs` 폴더 내에 스스로 하위 폴더를 생성하고, 적절한 마크다운(.md) 파일 이름으로 문서를 작성 및 업데이트합니다.
- **RAG (Retrieval-Augmented Generation)**: 사용자의 질문에 답하기 위해 인터넷 검색뿐만 아니라, `docs` 폴더에 자신이 기록해 둔 정보를 다시 찾아보고 답변합니다.

### 3. 보안 강화 (Security & Sandboxing)

- **파일 접근 제한**: OpenClaw 유형 에이전트의 보안 취약점을 해소하기 위해, 에이전트의 파일 읽기/쓰기 권한은 오직 `./docs` 디렉토리 내부로만 한정됩니다.
- 시스템의 다른 중요 파일이나 상위 디렉토리 접근은 원천적으로 차단됩니다.

### 4. 멀티 인터페이스 (Multi-Interface)

- **Web UI**: 직관적인 웹 인터페이스를 통해 에이전트와 대화하고, 실시간으로 생성되는 문서를 확인할 수 있습니다.
- **WhatsApp**: 모바일 메신저를 통해 언제 어디서든 에이전트에게 지시를 내리고 정보를 얻을 수 있습니다.

## 기술 스택 (Tech Stack)

- **Language**: Python 3.10+
- **AI Model**: Google Gemini Flash 2.5 Lite
- **Frameworks**: Streamlit (Web UI), Flask/FastAPI (WhatsApp Server)

## 디렉토리 구조

```text
my_agent/
├── docs/               # [Sandbox] 에이전트가 관리하는 유일한 저장소
│   ├── knowledge/      # (예시) 에이전트가 생성한 주제별 폴더
│   └── logs/           # (예시) 대화 기록 등
├── src/
│   ├── agent_core.py   # Gemini 및 Tool 로직
│   ├── web_ui.py       # 웹 인터페이스 구현체
│   └── whatsapp.py     # 왓츠앱 연동 모듈
├── .env                # API 키 설정 파일
└── README.md
```

## 시작하기 (Getting Started)

### 필수 조건 (Prerequisites)

- Python 3.10 이상
- Google Gemini API Key
- (선택) Google Search (Serper) API Key (인터넷 검색용)
- (선택) Twilio/Meta API Key (WhatsApp 연동용)

### 설치 (Installation)

1. 저장소 클론

   ```bash
   git clone https://github.com/your-username/my_agent.git
   cd my_agent
   ```

2. 의존성 패키지 설치

   ```bash
   uv pip install -r requirements.txt
   ```

3. 환경 변수 설정
   `.env` 파일을 생성하고 필요한 키를 입력합니다.

   ```ini
   GOOGLE_API_KEY=your_gemini_api_key
   SEARCH_API_KEY=your_serper_api_key
   # WhatsApp 사용 시
   WHATSAPP_TOKEN=your_token
   ```

## 사용 방법 (Usage)

### 웹 UI 모드

브라우저를 통해 에이전트와 대화하려면 다음 명령어를 실행하세요.

```bash
streamlit run src/web_ui.py
```

### WhatsApp 봇 모드

메신저 연동 서버를 실행하려면 다음 명령어를 실행하세요.

```bash
python src/whatsapp.py
```

## 라이선스

MIT License
