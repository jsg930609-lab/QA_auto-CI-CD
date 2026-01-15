# web/app.py 상단 부분 수정

from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
import threading
import json
import requests

# Playwright import
from playwright.async_api import async_playwright

# 프로젝트 루트 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from google_drive_reader import GoogleDriveReader
from test_case_manager import TestCaseManager
from openai_interpreter import OpenAITestCaseInterpreter
from playwright_executor import PlaywrightMCPExecutor
from report_generator import ReportGenerator

# ✨ config.py의 settings 객체 import
from config import settings as config  # ← 이렇게 수정!

app = Flask(__name__)
CORS(app)

# ✨ GitHub 설정
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_REPO = os.getenv("GITHUB_REPO", "")
GITHUB_WORKFLOW_ID = os.getenv("GITHUB_WORKFLOW_ID", "manual-test.yml")

# 전역 상태 관리
test_status = {
    "running": False,
    "progress": 0,
    "total": 0,
    "current_test": "",
    "results": [],
    "start_time": None,
    "end_time": None,
    "report_path": None
}

test_history = []

# 히스토리 파일 경로
HISTORY_FILE = Path(__file__).parent / "test_history.json"

def load_history():
    """히스토리 파일 로드"""
    global test_history
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                test_history = json.load(f)
        except Exception as e:
            print(f"히스토리 로드 오류: {e}")
            test_history = []

def save_history():
    """히스토리 파일 저장"""
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(test_history[-50:], f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"히스토리 저장 오류: {e}")

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')

@app.route('/api/test-cases')
def get_test_cases():
    """테스트 케이스 목록 조회"""
    try:
        print("=" * 60)
        print("테스트 케이스 로드 시작")
        print(f"GOOGLE_DRIVE_FILE_ID: {config.GOOGLE_DRIVE_FILE_ID}")
        
        if not config.GOOGLE_DRIVE_FILE_ID:
            print("⚠️ GOOGLE_DRIVE_FILE_ID가 설정되지 않았습니다")
            return jsonify([])
        
        # GoogleDriveReader 초기화
        print("GoogleDriveReader 초기화 중...")
        reader = GoogleDriveReader()
        
        print("테스트 케이스 읽기 중...")
        test_cases_raw = reader.read_test_cases_from_file(config.GOOGLE_DRIVE_FILE_ID)
        
        print(f"✅ {len(test_cases_raw)}개 테스트 케이스 로드 완료")
        
        # 첫 번째 테스트 케이스의 키 확인 (디버깅용)
        if test_cases_raw:
            print(f"테스트 케이스 키: {list(test_cases_raw[0].keys())}")
        
        # Dict를 정리해서 반환 (한글 키와 영문 키 모두 지원)
        result = []
        for i, tc in enumerate(test_cases_raw):
            # 다양한 키 이름 지원
            tc_dict = {
                "id": tc.get("id") or tc.get("시나리오 ID") or f"TC_{i+1}",
                "title": (
                    tc.get("title") or 
                    tc.get("제목") or 
                    tc.get("테스트 케이스명") or 
                    f"테스트 케이스 #{i+1}"
                ),
                "url": (
                    tc.get("url") or 
                    tc.get("URL") or 
                    tc.get("Link") or 
                    ""
                ),
                "steps": (
                    tc.get("steps") or 
                    tc.get("Test step") or 
                    tc.get("테스트 단계") or 
                    []
                ),
                "expected": (
                    tc.get("expected") or 
                    tc.get("Expected Result") or 
                    tc.get("예상 결과") or 
                    ""
                ),
                "status": (
                    tc.get("status") or 
                    tc.get("상태") or 
                    "NEW"
                ),
                # 추가 정보
                "category": tc.get("대분류", ""),
                "subcategory": tc.get("소분류", ""),
                "precondition": tc.get("Pre-condition", "")
            }
            result.append(tc_dict)
        
        print(f"✅ {len(result)}개 테스트 케이스 변환 완료")
        
        # 첫 번째 결과 샘플 출력 (디버깅용)
        if result:
            print(f"변환된 첫 번째 케이스: ID={result[0]['id']}, 제목={result[0]['title']}")
        
        print("=" * 60)
        
        return jsonify(result)
    
    except Exception as e:
        print("=" * 60)
        print(f"❌ 테스트 케이스 로드 오류: {e}")
        
        import traceback
        traceback.print_exc()
        
        print("=" * 60)
        print("⚠️ 샘플 데이터 반환")
        
        return jsonify([
            {
                "id": "SAMPLE_001",
                "title": "샘플 테스트 - Google Sheets 연결 실패",
                "url": "https://example.com",
                "steps": ["샘플 단계 1", "샘플 단계 2"],
                "expected": "샘플 결과",
                "status": "NEW"
            }
        ])

@app.route('/api/stats')
def get_stats():
    """통계 정보 조회"""
    try:
        passed = sum(1 for r in test_status["results"] if r.get("status") == "PASS")
        failed = sum(1 for r in test_status["results"] if r.get("status") == "FAIL")
        skipped = sum(1 for r in test_status["results"] if r.get("status") == "SKIP")
        total = len(test_status["results"])
        
        return jsonify({
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/history')
def get_history():
    """실행 히스토리 조회"""
    return jsonify(test_history[-10:])

@app.route('/api/test-status')
def get_test_status():
    """현재 테스트 실행 상태 조회"""
    return jsonify(test_status)

@app.route('/api/run-tests', methods=['POST'])
def run_tests():
    """테스트 실행"""
    if test_status["running"]:
        return jsonify({"error": "이미 테스트가 실행 중입니다"}), 400
    
    thread = threading.Thread(target=run_tests_async)
    thread.start()
    
    return jsonify({"message": "테스트 실행 시작"})

def run_tests_async():
    """비동기 테스트 실행"""
    asyncio.run(execute_tests())

async def execute_tests():
    """실제 테스트 실행"""
    global test_status, test_history
    
    try:
        test_status["running"] = True
        test_status["progress"] = 0
        test_status["results"] = []
        test_status["start_time"] = datetime.now().isoformat()
        
        # Google Sheets에서 테스트 케이스 읽기
        reader = GoogleDriveReader()
        # ✨ read_test_cases_from_file 사용
        test_cases_raw = reader.read_test_cases_from_file(config.GOOGLE_DRIVE_FILE_ID)
        
        # TestCaseManager가 Dict 리스트를 받는지, TestCase 객체를 받는지 확인 필요
        # 일단 Dict를 TestCase로 변환
        from models import TestCase
        
        test_cases = []
        for tc_dict in test_cases_raw:
            try:
                # Dict를 TestCase 객체로 변환
                test_case = TestCase(
                    id=tc_dict.get("id", 0),
                    title=tc_dict.get("title", ""),
                    url=tc_dict.get("url", ""),
                    steps=tc_dict.get("steps", []),
                    expected=tc_dict.get("expected", ""),
                    status=tc_dict.get("status", "NEW")
                )
                test_cases.append(test_case)
            except Exception as e:
                print(f"테스트 케이스 변환 오류: {e}")
                continue
        
        test_status["total"] = len(test_cases)
        test_status["current_test"] = "테스트 케이스 처리 중..."
        
        # TestCaseManager로 처리
        manager = TestCaseManager(test_cases)
        
        # OpenAI로 보정
        interpreter = OpenAITestCaseInterpreter()
        corrected = await interpreter.correct_test_cases_batch(manager.test_cases)
        manager.test_cases = corrected
        
        test_status["progress"] = 10
        
        # Playwright 실행
        async with async_playwright() as p:
            executor = PlaywrightMCPExecutor(p)
            
            for i, test_case in enumerate(manager.test_cases):
                test_status["current_test"] = f"{test_case.title}"
                
                result = await executor.execute_test(test_case)
                test_status["results"].append({
                    "id": test_case.id,
                    "title": test_case.title,
                    "status": "PASS" if result.success else "FAIL",
                    "error": result.error_message
                })
                
                test_status["progress"] = int((i + 1) / len(manager.test_cases) * 90) + 10
        
        # 리포트 생성
        test_status["current_test"] = "리포트 생성 중..."
        generator = ReportGenerator()
        report_path = generator.generate_html_report(
            manager.test_cases,
            [r for r in test_status["results"]]
        )
        
        test_status["report_path"] = f"/reports/{Path(report_path).name}"
        test_status["progress"] = 100
        test_status["end_time"] = datetime.now().isoformat()
        
        # 히스토리 저장
        passed = sum(1 for r in test_status["results"] if r["status"] == "PASS")
        failed = sum(1 for r in test_status["results"] if r["status"] == "FAIL")
        skipped = sum(1 for r in test_status["results"] if r["status"] == "SKIP")
        
        test_history.append({
            "timestamp": test_status["start_time"],
            "total": len(test_status["results"]),
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "report_path": test_status["report_path"]
        })
        
        save_history()
        
    except Exception as e:
        print(f"테스트 실행 오류: {e}")
        import traceback
        traceback.print_exc()
        test_status["current_test"] = f"오류 발생: {str(e)}"
    
    finally:
        test_status["running"] = False

@app.route('/api/reports')
def get_reports():
    """리포트 목록 조회"""
    try:
        reports_dir = Path(__file__).parent.parent / "reports"
        
        if not reports_dir.exists():
            return jsonify([])
        
        reports = []
        for report_file in sorted(reports_dir.glob("*.html"), reverse=True)[:10]:
            stat = report_file.stat()
            reports.append({
                "filename": report_file.name,
                "path": str(report_file),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "size": stat.st_size
            })
        
        return jsonify(reports)
    
    except Exception as e:
        print(f"리포트 로드 오류: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/reports/<path:filename>')
def serve_report(filename):
    """리포트 파일 제공"""
    report_path = Path(__file__).parent.parent / "reports" / filename
    
    if report_path.exists():
        return send_file(report_path)
    
    return jsonify({"error": f"리포트를 찾을 수 없습니다: {filename}"}), 404

# ✨ GitHub Actions 트리거
@app.route('/api/trigger-github-actions', methods=['POST'])
def trigger_github_actions():
    """GitHub Actions 워크플로우 트리거"""
    
    if not GITHUB_TOKEN or not GITHUB_REPO:
        return jsonify({
            "error": "GitHub 설정이 필요합니다. GITHUB_TOKEN과 GITHUB_REPO를 .env에 추가하세요."
        }), 400
    
    try:
        data = request.json or {}
        
        url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/workflows/{GITHUB_WORKFLOW_ID}/dispatches"
        
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        payload = {
            "ref": "main",
            "inputs": {
                "test_environment": data.get("environment", "production"),
                "test_suite": data.get("test_suite", "all"),
                "browser": data.get("browser", "chromium")
            }
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 204:
            return jsonify({
                "success": True,
                "message": "GitHub Actions 워크플로우가 트리거되었습니다.",
                "url": f"https://github.com/{GITHUB_REPO}/actions"
            })
        else:
            return jsonify({
                "error": f"GitHub API 오류: {response.status_code}",
                "details": response.text
            }), response.status_code
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✨ GitHub Actions 상태 조회
@app.route('/api/github-actions-status')
def get_github_actions_status():
    """최근 GitHub Actions 실행 상태 조회"""
    
    if not GITHUB_TOKEN or not GITHUB_REPO:
        return jsonify([])
    
    try:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/runs"
        
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        params = {"per_page": 5}
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            runs = []
            
            for run in data.get("workflow_runs", []):
                runs.append({
                    "id": run["id"],
                    "name": run["name"],
                    "status": run["status"],
                    "conclusion": run["conclusion"],
                    "created_at": run["created_at"],
                    "updated_at": run["updated_at"],
                    "html_url": run["html_url"]
                })
            
            return jsonify(runs)
        else:
            return jsonify([])
    
    except Exception as e:
        print(f"GitHub Actions 상태 조회 오류: {e}")
        return jsonify([])

if __name__ == '__main__':
    # 필요한 디렉토리 생성
    Path("web/static/css").mkdir(parents=True, exist_ok=True)
    Path("web/static/js").mkdir(parents=True, exist_ok=True)
    Path("web/templates").mkdir(parents=True, exist_ok=True)
    
    # 히스토리 로드
    load_history()
    
    print("=" * 60)
    print("QA 테스트 자동화 웹 대시보드")
    print("=" * 60)
    print("\n🌐 서버 시작: http://localhost:5000")
    
    if GITHUB_TOKEN and GITHUB_REPO:
        print(f"✅ GitHub Actions 연동: {GITHUB_REPO}")
    else:
        print("⚠️  GitHub Actions 미연동")
        print("   (.env에 GITHUB_TOKEN, GITHUB_REPO 추가 필요)")
    
    print("\n브라우저에서 http://localhost:5000 을 열어주세요\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)