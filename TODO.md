# TODO List for my_agent

## 1. 환경 설정 (Environment Setup)

- [x] `pyproject.toml`에 `ollama` 또는 `openai` 라이브러리 추가 및 `uv sync` 실행
- [x] `.env.sample`에 Ollama 관련 설정 추가 (`AI_PROVIDER`, `OLLAMA_BASE_URL`, `OLLAMA_MODEL_NAME`)
- [x] `.env` 파일에 실제 Ollama 연동 정보 설정

## 2. 모델 추상화 및 리팩토링 (Refactoring & Abstraction)

- [x] `src/agent_core.py`에서 `MyAgent` 클래스를 추상화하여 다양한 프로바이더를 지원하도록 구조 변경
  - [x] 공통 인터페이스 정의 (예: `send_message`, `create_session`)
  - [x] `GeminiProvider` 구현 (기존 로직 이동)
  - [x] `OllamaProvider` 구현 (OpenAI 호환 API 또는 Ollama SDK 사용)
- [x] 프로바이더별로 도구(Tools) 호출 방식 차이 해결
  - [x] 파이썬 함수를 Ollama/OpenAI가 이해할 수 있는 JSON Schema 형식으로 변환하는 유틸리티 작성
  - [x] Ollama의 경우 자동 함수 호출(Automatic Function Calling) 루프를 `MyAgent` 내에 직접 구현

## 3. Ollama (gpt-oss) 연동 구현 (Ollama Implementation)

- [x] Ollama API를 이용한 메시지 전송 및 응답 수신 로직 작성
- [x] 대화 기록(Chat History)을 관리하는 세션 객체 구현 (Gemini의 `chats.create()`와 유사한 인터페이스)
- [x] 모델 응답에 포함된 도구 호출(Tool Call)을 해석하고 실행한 뒤 다시 모델에게 전달하는 루프 구현

## 4. 통합 및 테스트 (Integration & Testing)

- [ ] `src/telegram_bot.py`와 `src/web_ui.py`에서 변경된 `MyAgent`를 정상적으로 사용할 수 있도록 인터페이스 호환성 확인
  - [ ] 응답 객체의 구조(`response.text`, `response.candidates` 등)가 기존과 호환되도록 래핑(Wrapping) 처리
- [ ] `AI_PROVIDER` 환경 변수에 따라 Gemini와 Ollama가 정상적으로 교체되는지 확인
- [ ] Ollama 환경에서 도구(Tools)들이 정상적으로 호출되고 결과가 반영되는지 테스트

## 5. 문서화 (Documentation)

- [ ] `README.md`에 Ollama 사용 방법 및 필요한 환경 변수 설명 추가
- [ ] `openclaw.md` 또는 관련 문서에 아키텍처 변경 사항 기록
