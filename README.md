# QA 테스트 자동화 시스템

Google Drive에서 테스트케이스를 읽어와 OpenAI API로 해석한 후, Playwright MCP를 통해 실제 브라우저에서 자동으로 테스트를 수행하는 시스템입니다.

## 주요 기능

1. **Google Drive 연동**: Google Drive에서 테스트케이스를 읽어옵니다 (Google Sheets, Google Docs, CSV, JSON 지원)
2. **AI 기반 해석**: OpenAI API를 사용하여 테스트케이스를 실행 가능한 형태로 해석합니다
3. **브라우저 자동화**: Playwright MCP를 통해 실제 브라우저에서 테스트를 실행합니다
4. **결과 리포트**: 테스트 결과를 JSON, HTML, Excel 형식으로 리포트를 생성합니다
5. **실패 케이스 추적**: 실패하거나 미수행된 케이스는 별도로 표시하여 QA 팀의 후속 검토를 지원합니다

## 시스템 요구사항

- Python 3.8 이상
- Google Drive API 인증 파일 (`credentials.json`)
- OpenAI API 키
- Playwright MCP 서버 (실행 중이어야 함)

## 설치

1. 저장소 클론:
```bash
git clone <repository-url>
cd Cursor-qa_auto
```

2. 가상환경 생성 및 활성화:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. 의존성 설치:
```bash
pip install -r requirements.txt
```

4. Playwright 브라우저 설치:
```bash
playwright install
```

## 설정

1. `.env` 파일 생성 (`.env.example` 참고):
```bash
cp .env.example .env
```

2. `.env` 파일 편집하여 다음 정보 입력:
   - `GOOGLE_DRIVE_FILE_ID` 또는 `GOOGLE_DRIVE_FOLDER_ID`: 테스트케이스가 있는 Google Drive 파일/폴더 ID
   - `OPENAI_API_KEY`: OpenAI API 키
   - `PLAYWRIGHT_MCP_SERVER_URL`: Playwright MCP 서버 URL (기본값: http://localhost:3000)

3. Google Drive API 인증 설정:
   - [Google Cloud Console](https://console.cloud.google.com/)에서 프로젝트 생성
   - Google Drive API 활성화
   - OAuth 2.0 클라이언트 ID 생성
   - `credentials.json` 파일을 프로젝트 루트에 저장

## 사용 방법

### 기본 실행

```bash
python main.py
```

### 실행 흐름

1. **테스트케이스 읽기**: Google Drive에서 테스트케이스를 읽어옵니다
2. **테스트케이스 해석**: OpenAI API가 각 테스트케이스의 목적과 조건을 해석합니다
3. **테스트 실행**: Playwright MCP가 실제 브라우저에서 테스트를 수행합니다
4. **결과 리포트**: 테스트 결과를 리포트로 생성하고, 실패/미수행 케이스를 출력합니다

## 프로젝트 구조

```
Cursor-qa_auto/
├── main.py                  # 메인 실행 스크립트
├── config.py                # 설정 파일
├── google_drive_reader.py   # Google Drive 연동 모듈
├── openai_interpreter.py    # OpenAI API 해석 모듈
├── playwright_executor.py   # Playwright MCP 실행 모듈
├── report_generator.py      # 리포트 생성 모듈
├── requirements.txt         # Python 의존성
├── .env                     # 환경 변수 (생성 필요)
├── credentials.json         # Google Drive 인증 파일 (생성 필요)
├── screenshots/             # 실패 시 스크린샷 저장 디렉토리
└── reports/                 # 테스트 리포트 저장 디렉토리
```

## 테스트케이스 형식

Google Drive에서 읽어올 테스트케이스는 다음 형식을 권장합니다:

### Google Sheets 형식 예시

| 제목 | 목적 | 전제조건 | 단계 | 기대 결과 |
|------|------|----------|------|----------|
| 로그인 테스트 | 사용자가 로그인할 수 있는지 확인 | 계정이 존재해야 함 | 1. 로그인 페이지 이동<br>2. 이메일 입력<br>3. 비밀번호 입력<br>4. 로그인 버튼 클릭 | 로그인 성공 메시지 표시 |

### JSON 형식 예시

```json
[
  {
    "제목": "로그인 테스트",
    "목적": "사용자가 로그인할 수 있는지 확인",
    "전제조건": "계정이 존재해야 함",
    "단계": "1. 로그인 페이지 이동\n2. 이메일 입력\n3. 비밀번호 입력\n4. 로그인 버튼 클릭",
    "기대 결과": "로그인 성공 메시지 표시"
  }
]
```

## 리포트 형식

시스템은 다음 형식의 리포트를 생성합니다:

- **JSON**: 구조화된 데이터 형식
- **HTML**: 시각적인 웹 리포트 (기본값)
- **Excel**: 스프레드시트 형식

리포트 형식은 `.env` 파일의 `REPORT_FORMAT` 설정으로 변경할 수 있습니다.

## 실패 케이스 처리

실패하거나 미수행된 테스트케이스는:
1. 콘솔에 상세 정보가 출력됩니다
2. 리포트에 별도로 표시됩니다
3. 스크린샷이 자동으로 저장됩니다 (설정된 경우)

QA 팀은 이 정보를 바탕으로 후속 검토를 진행할 수 있습니다.

## 문제 해결

### Google Drive 인증 오류
- `credentials.json` 파일이 올바른 위치에 있는지 확인
- Google Cloud Console에서 OAuth 동의 화면이 설정되었는지 확인
- 필요한 스코프가 요청되었는지 확인

### OpenAI API 오류
- API 키가 올바른지 확인
- API 사용량 한도를 확인
- 모델 이름이 올바른지 확인

### Playwright MCP 연결 오류
- MCP 서버가 실행 중인지 확인
- 서버 URL이 올바른지 확인
- 네트워크 연결 상태 확인

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

## 기여

버그 리포트나 기능 제안은 이슈로 등록해주세요.

