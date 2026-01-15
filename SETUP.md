# 설정 가이드

## 1. Google Drive API 설정

### 1.1 Google Cloud Console 설정

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. **API 및 서비스** > **라이브러리**로 이동
4. "Google Drive API" 검색 후 활성화
5. **API 및 서비스** > **사용자 인증 정보**로 이동
6. **사용자 인증 정보 만들기** > **OAuth 클라이언트 ID** 선택
7. 애플리케이션 유형: **데스크톱 앱** 선택
8. 생성된 클라이언트 ID의 JSON 파일을 다운로드
9. 다운로드한 파일을 `credentials.json`으로 이름 변경 후 프로젝트 루트에 저장

### 1.2 Google Drive 파일/폴더 ID 확인

1. Google Drive에서 테스트케이스 파일 또는 폴더 열기
2. URL에서 파일/폴더 ID 확인
   - 예: `https://drive.google.com/drive/folders/1ABC123xyz...`
   - ID는 `/folders/` 또는 `/file/d/` 뒤의 문자열
3. `.env` 파일에 `GOOGLE_DRIVE_FILE_ID` 또는 `GOOGLE_DRIVE_FOLDER_ID` 설정

## 2. OpenAI API 설정

1. [OpenAI Platform](https://platform.openai.com/) 접속
2. API 키 생성 (Settings > API keys)
3. `.env` 파일에 `OPENAI_API_KEY` 설정

## 3. Playwright MCP 서버 설정

### 3.1 MCP 서버 실행

Playwright MCP 서버가 실행 중이어야 합니다. 서버 URL을 `.env` 파일에 설정하세요.

```env
PLAYWRIGHT_MCP_SERVER_URL=http://localhost:3000
```

### 3.2 MCP 서버 API 구조

현재 코드는 표준 HTTP REST API 형식을 가정하고 있습니다. 실제 MCP 서버가 다른 프로토콜을 사용하는 경우 `playwright_executor.py`의 다음 메서드를 수정해야 합니다:

- `_create_context()`: 브라우저 컨텍스트 생성
- `_execute_action()`: 액션 실행
- `_take_screenshot()`: 스크린샷 촬영
- `_close_context()`: 컨텍스트 종료

## 4. 환경 변수 설정

`.env` 파일을 생성하고 다음 내용을 입력하세요:

```env
# Google Drive 설정
GOOGLE_DRIVE_CREDENTIALS_FILE=credentials.json
GOOGLE_DRIVE_TOKEN_FILE=token.json
GOOGLE_DRIVE_FOLDER_ID=your_folder_id_here
GOOGLE_DRIVE_FILE_ID=your_file_id_here

# OpenAI 설정
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_MAX_TOKENS=2000

# Playwright MCP 설정
PLAYWRIGHT_MCP_SERVER_URL=http://localhost:3000
PLAYWRIGHT_BROWSER=chromium

# 테스트 설정
TEST_TIMEOUT=30000
SCREENSHOT_ON_FAILURE=true
SCREENSHOT_DIR=screenshots

# 리포트 설정
REPORT_DIR=reports
REPORT_FORMAT=html
```

## 5. 첫 실행

1. 모든 설정이 완료되었는지 확인
2. Playwright MCP 서버가 실행 중인지 확인
3. 다음 명령어로 실행:

```bash
python main.py
```

첫 실행 시 Google Drive 인증을 위해 브라우저가 열리고 OAuth 인증을 진행해야 합니다. 인증 완료 후 `token.json` 파일이 생성됩니다.

