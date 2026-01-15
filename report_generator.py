"""
테스트 결과 리포트 생성
"""
import os
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path
import config


class ReportGenerator:
    """테스트 결과 리포트 생성 클래스"""
    
    def __init__(self):
        self.report_dir = config.settings.REPORT_DIR
        self.report_format = config.settings.REPORT_FORMAT
        
        # 리포트 디렉토리 생성
        Path(self.report_dir).mkdir(parents=True, exist_ok=True)
    
    def generate_report(self, test_results: List[Dict[str, Any]]) -> str:
        """
        테스트 결과 리포트 생성
        
        Args:
            test_results: 테스트 실행 결과 리스트
            
        Returns:
            생성된 리포트 파일 경로
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if self.report_format == "html":
            return self._generate_html_report(test_results, timestamp)
        elif self.report_format == "json":
            return self._generate_json_report(test_results, timestamp)
        else:
            return self._generate_html_report(test_results, timestamp)
    
    def get_failed_cases(self, test_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """실패하거나 미수행된 케이스 추출"""
        return [
            result for result in test_results
            if result.get("status") in ["failed", "error", "skipped"]
        ]
    
    def _generate_html_report(self, test_results: List[Dict[str, Any]], timestamp: str) -> str:
        """HTML 형식 리포트 생성"""
        # 통계 계산
        total = len(test_results)
        passed = sum(1 for r in test_results if r.get("status") == "passed")
        failed = sum(1 for r in test_results if r.get("status") == "failed")
        skipped = sum(1 for r in test_results if r.get("status") == "skipped")
        error = sum(1 for r in test_results if r.get("status") == "error")
        
        # HTML 생성
        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QA 테스트 리포트 - {timestamp}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f7fa;
            padding: 20px;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 32px;
            margin-bottom: 10px;
        }}
        
        .header .timestamp {{
            opacity: 0.9;
            font-size: 14px;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        
        .stat-card .number {{
            font-size: 36px;
            font-weight: bold;
            margin: 10px 0;
        }}
        
        .stat-card .label {{
            color: #6c757d;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .stat-card.total .number {{ color: #667eea; }}
        .stat-card.passed .number {{ color: #28a745; }}
        .stat-card.failed .number {{ color: #dc3545; }}
        .stat-card.skipped .number {{ color: #ffc107; }}
        .stat-card.error .number {{ color: #fd7e14; }}
        
        .test-cases {{
            padding: 30px;
        }}
        
        .test-case {{
            border: 1px solid #e9ecef;
            border-radius: 8px;
            margin-bottom: 20px;
            overflow: hidden;
        }}
        
        .test-case-header {{
            padding: 20px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: background 0.2s;
        }}
        
        .test-case-header:hover {{
            background: #f8f9fa;
        }}
        
        .test-case-header.passed {{
            background: #d4edda;
            border-left: 4px solid #28a745;
        }}
        
        .test-case-header.failed {{
            background: #f8d7da;
            border-left: 4px solid #dc3545;
        }}
        
        .test-case-header.error {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
        }}
        
        .test-case-title {{
            font-size: 18px;
            font-weight: 600;
        }}
        
        .test-case-status {{
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }}
        
        .status-passed {{
            background: #28a745;
            color: white;
        }}
        
        .status-failed {{
            background: #dc3545;
            color: white;
        }}
        
        .status-error {{
            background: #ffc107;
            color: black;
        }}
        
        .test-case-details {{
            padding: 20px;
            background: #f8f9fa;
            border-top: 1px solid #e9ecef;
        }}
        
        .detail-section {{
            margin-bottom: 15px;
        }}
        
        .detail-label {{
            font-weight: 600;
            color: #495057;
            margin-bottom: 5px;
        }}
        
        .detail-value {{
            color: #6c757d;
            padding-left: 10px;
        }}
        
        .error-message {{
            background: #fff3cd;
            border-left: 3px solid #ffc107;
            padding: 10px 15px;
            margin-top: 10px;
            border-radius: 4px;
        }}
        
        .steps {{
            margin-top: 10px;
        }}
        
        .step {{
            padding: 8px 12px;
            margin: 5px 0;
            border-radius: 4px;
            font-size: 14px;
        }}
        
        .step.success {{
            background: #d4edda;
            border-left: 3px solid #28a745;
        }}
        
        .step.failed {{
            background: #f8d7da;
            border-left: 3px solid #dc3545;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>QA 테스트 리포트</h1>
            <div class="timestamp">생성 시간: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
        </div>
        
        <div class="stats">
            <div class="stat-card total">
                <div class="label">전체 테스트</div>
                <div class="number">{total}</div>
            </div>
            <div class="stat-card passed">
                <div class="label">성공</div>
                <div class="number">{passed}</div>
            </div>
            <div class="stat-card failed">
                <div class="label">실패</div>
                <div class="number">{failed}</div>
            </div>
            <div class="stat-card skipped">
                <div class="label">스킵</div>
                <div class="number">{skipped}</div>
            </div>
            <div class="stat-card error">
                <div class="label">오류</div>
                <div class="number">{error}</div>
            </div>
        </div>
        
        <div class="test-cases">
            <h2 style="margin-bottom: 20px;">테스트 케이스 상세</h2>
"""
        
        # 각 테스트 케이스 추가
        for i, result in enumerate(test_results, 1):
            status = result.get("status", "unknown")
            test_case = result.get("test_case", {})
            original = test_case.get("original", {})
            interpretation = result.get("interpretation", {})
            
            title = original.get("제목", f"테스트 케이스 {i}")
            test_id = original.get("시나리오 ID", f"TC_{i}")
            purpose = interpretation.get("purpose", "N/A") if interpretation else "해석 실패"
            error = result.get("error", "")
            duration = result.get("duration", 0)
            
            status_class = status.replace("_", "-")
            status_label = {
                "passed": "성공",
                "failed": "실패",
                "error": "오류",
                "skipped": "스킵"
            }.get(status, status.upper())
            
            html_content += f"""
            <div class="test-case">
                <div class="test-case-header {status}">
                    <div>
                        <div class="test-case-title">{i}. {title}</div>
                        <div style="font-size: 14px; color: #6c757d; margin-top: 5px;">ID: {test_id}</div>
                    </div>
                    <div class="test-case-status status-{status}">{status_label}</div>
                </div>
                <div class="test-case-details">
                    <div class="detail-section">
                        <div class="detail-label">목적</div>
                        <div class="detail-value">{purpose}</div>
                    </div>
"""
            
            if error:
                html_content += f"""
                    <div class="detail-section">
                        <div class="detail-label">오류</div>
                        <div class="error-message">{error}</div>
                    </div>
"""
            
            # 단계별 실행 결과
            steps_executed = result.get("steps_executed", [])
            steps_failed = result.get("steps_failed", [])
            
            if steps_executed or steps_failed:
                html_content += """
                    <div class="detail-section">
                        <div class="detail-label">실행 단계</div>
                        <div class="steps">
"""
                
                for step in steps_executed:
                    action = step.get("action", "")
                    target = step.get("target", "")
                    html_content += f"""
                            <div class="step success">✓ {action}: {target}</div>
"""
                
                for step in steps_failed:
                    action = step.get("action", "")
                    target = step.get("target", "")
                    step_error = step.get("error", "")
                    html_content += f"""
                            <div class="step failed">✗ {action}: {target}<br><small>{step_error}</small></div>
"""
                
                html_content += """
                        </div>
                    </div>
"""
            
            html_content += f"""
                    <div class="detail-section">
                        <div class="detail-label">실행 시간</div>
                        <div class="detail-value">{duration:.2f}초</div>
                    </div>
                </div>
            </div>
"""
        
        html_content += """
        </div>
    </div>
</body>
</html>
"""
        
        # 파일 저장
        report_path = os.path.join(self.report_dir, f"test_report_{timestamp}.html")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return report_path
    
    def _generate_json_report(self, test_results: List[Dict[str, Any]], timestamp: str) -> str:
        """JSON 형식 리포트 생성"""
        import json
        
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": len(test_results),
                "passed": sum(1 for r in test_results if r.get("status") == "passed"),
                "failed": sum(1 for r in test_results if r.get("status") == "failed"),
                "skipped": sum(1 for r in test_results if r.get("status") == "skipped"),
                "error": sum(1 for r in test_results if r.get("status") == "error")
            },
            "results": test_results
        }
        
        report_path = os.path.join(self.report_dir, f"test_report_{timestamp}.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        return report_path