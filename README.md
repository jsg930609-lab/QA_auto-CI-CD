> Google Sheets 연동 + Open AI API + Playwright 기반 웹 테스트 자동화 시스템

## 🎯 프로젝트 개요
- 바이브 코딩을 통한 QA 자동화 연구
- QA 엔지니어를 위한 테스트 자동화 웹 대시보드
- Google Sheets에서 테스트 케이스를 관리하고, OpenAI API가 각 테스트 케이스의 목적과 조건을 해석해 Playwright로 테스트를 실행하며, 실시간 결과를 웹에서 확인할 수 있습니다.

## ✨ 주요 기능

### 📊 실시간 대시보드
- 테스트 케이스 현황 및 통계 실시간 표시
- 검색 및 필터링 기능
- 반응형 웹 디자인

### 🔄 Google Sheets 연동
- Service Account 기반 자동 동기화
- 테스트 케이스 실시간 로드
- 양방향 데이터 연동

### 🤖 자동화 실행
- Playwright 기반 브라우저 자동화
- 실시간 진행률 표시
- 성공/실패 결과 자동 수집

### 📈 리포트 생성
- HTML 형식의 상세 테스트 리포트
- 테스트 케이스별 결과 분석
- 히스토리 자동 기록 및 관리

### 🔄 GitHub Actions 연동
- CI/CD 파이프라인 통합
- 워크플로우 원격 트리거
- 실행 히스토리 조회

## 🛠️ 기술 스택

### Backend
- **Python 3.11+**: 메인 언어
- **Flask 3.0+**: 웹 서버 프레임워크
- **Google Sheets API**: 테스트 케이스 관리
- **Playwright**: 브라우저 자동화
- **asyncio**: 비동기 처리

### Frontend
- **Vanilla JavaScript**: 프론트엔드 로직
- **HTML5/CSS3**: UI 구성
- **Responsive Design**: 모바일 지원

### DevOps
- **GitHub Actions**: CI/CD 파이프라인
- **Google Service Account**: 인증 및 권한 관리
## 📸 스크린샷

### 메인 대시보드
<img width="1286" height="897" alt="dashboard" src="https://github.com/user-attachments/assets/930bbb82-ce1b-407c-98c0-571d82f313f5" />

### 테스트 케이스
<img width="1272" height="890" alt="testcase" src="https://github.com/user-attachments/assets/b746d1c4-e1cb-4881-8534-f2d43191582f" />

### 진행 프로그레스바
<img width="954" height="699" alt="progressbar" src="https://github.com/user-attachments/assets/a2bb7c1e-f462-4cbe-829a-b8042a200bf6" />

### 실행 히스토리 & 리포트
<img width="1291" height="891" alt="history" src="https://github.com/user-attachments/assets/704214ba-3036-4f19-aeb9-d11c7fc7b110" />
<img width="1255" height="859" alt="history_detail" src="https://github.com/user-attachments/assets/fe5d7b93-e4ce-4bd1-82b1-bee5b23cda2c" />

### CD/CD
<img width="1282" height="896" alt="CICD" src="https://github.com/user-attachments/assets/14ace4e0-acf0-4afe-8cf3-02fbe183c975" />


## 📁 프로젝트 구조
```
QA_auto-CI-CD/
├── web/
│   ├── app.py                # Flask 서버
│   ├── static/
│   │   ├── js/
│   │   │   └── main.js       # 프론트엔드 로직
│   │   └── css/
│   │       └── style.css     # 스타일시트
│   ├── templates/
│   │   └── index.html        # 메인 페이지
│   └── test_history.json     # 실행 히스토리
├── reports/                  # 테스트 리포트
├── screenshots/              # README 스크린샷
├── google_drive_reader.py    # Google Sheets 연동
├── config.py                 # 설정 관리
├── credentials.json          # Service Account 키
├── .env                      # 환경 변수
├── .gitignore
├── requirements.txt
└── README.md
```

## 📊 성과

- ✅ 테스트 케이스 자동화
- ✅ 수동 테스트 대비 **70% 시간 단축**
- ✅ 실행 히스토리 자동 기록
- ✅ 100% 성공률 달성

## 🔧 향후 개선 계획

- [ ] 테스트 케이스 개별 선택 실행
- [ ] 다중 브라우저 동시 실행 (Chrome, Firefox, Safari)
- [ ] Slack/Discord 알림 연동
- [ ] 테스트 케이스 스케줄링
- [ ] 실패 시 스크린샷 자동 첨부
- [ ] 대시보드 실시간 업데이트 (WebSocket)

## 👨‍💻 개발자

**맥스** - QA Engineer  
- GitHub: [@jsg930609-lab](https://github.com/jsg930609-lab)
