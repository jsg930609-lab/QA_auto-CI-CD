<img width="1302" height="892" alt="image" src="https://github.com/user-attachments/assets/4c7d01bd-dd42-4902-bcf9-2ed68f33cf14" /># QA 테스트 자동화 웹 대시보드

> Google Sheets 연동 + Playwright 기반 웹 테스트 자동화 시스템

## 🎯 프로젝트 개요
- 바이브 코딩을 통한 QA 자동화 연구
- QA 엔지니어를 위한 테스트 자동화 웹 대시보드
- Google Sheets에서 테스트 케이스를 관리하고, OpenAI API가 각 테스트 케이스의 목적과 조건을 해석해 Playwright로 테스트를 실행하며, 실시간 결과를 웹에서 확인할 수 있습니다.

## ✨ 주요 기능

- 📊 **Google Sheets 연동**: Service Account 기반 실시간 데이터 동기화
- 🤖 **Playwright 자동화**: 크로스 브라우저 테스트 자동 실행
- 📈 **실시간 대시보드**: Flask 기반 웹 UI로 테스트 현황 모니터링
- 📝 **리포트 생성**: HTML 형식의 상세 테스트 리포트
- 🔄 **GitHub Actions 연동**: CI/CD 파이프라인 통합

## 🛠️ 기술 스택

### Backend
- Python 3.11+
- Flask (웹 서버)
- Google Sheets API
- Playwright (브라우저 자동화)

### Frontend  
- Vanilla JavaScript
- HTML5/CSS3
- Responsive Design

### DevOps
- GitHub Actions
- Google Service Account

## 📸 스크린샷

### 메인 대시보드
<img width="1286" height="897" alt="dashboard" src="https://github.com/user-attachments/assets/930bbb82-ce1b-407c-98c0-571d82f313f5" />

### 테스트 케이스
<img width="1272" height="890" alt="testcase" src="https://github.com/user-attachments/assets/b746d1c4-e1cb-4881-8534-f2d43191582f" />

### 실행 히스토리 & 리포트
<img width="1291" height="891" alt="history" src="https://github.com/user-attachments/assets/704214ba-3036-4f19-aeb9-d11c7fc7b110" />
<img width="1255" height="859" alt="history_detail" src="https://github.com/user-attachments/assets/fe5d7b93-e4ce-4bd1-82b1-bee5b23cda2c" />

### CD/CD
<img width="1282" height="896" alt="CICD" src="https://github.com/user-attachments/assets/14ace4e0-acf0-4afe-8cf3-02fbe183c975" />


## 📋 프로젝트 구조
```
QA_auto-CI-CD/
├── web/
│   ├── app.py                 # Flask 서버
│   ├── static/
│   │   ├── js/main.js        # 프론트엔드 로직
│   │   └── css/style.css     # 스타일
│   └── templates/
│       └── index.html         # 메인 페이지
├── google_drive_reader.py     # Google Sheets 연동
├── playwright_executor.py     # Playwright 실행
├── report_generator.py        # 리포트 생성
├── credentials.json           # Service Account 키
├── .env                       # 환경 변수
└── requirements.txt
```

## 📊 성과

- ✅ 테스트 케이스 자동화
- ✅ 수동 테스트 대비 **70% 시간 단축**
- ✅ 실행 히스토리 자동 기록
- ✅ 100% 성공률 달성

## 🔧 향후 개선 계획

- [ ] 다중 브라우저 동시 실행
- [ ] Slack/Discord 알림 연동
- [ ] 테스트 케이스 스케줄링
- [ ] 대시보드 실시간 업데이트 (WebSocket)

## 👨‍💻 개발자

**맥스** - QA Engineer  
- GitHub: [@jsg930609-lab](https://github.com/jsg930609-lab)

## 📄 라이선스

MIT License
