"""
QA 테스트 자동화 메인 실행 스크립트

실행 흐름:
1. Google Drive에서 테스트케이스 읽기
1.5. 테스트케이스 자동 생성/보정 (NEW!)
2. OpenAI API로 테스트케이스 해석 (배치 처리)
3. Playwright로 테스트 실행
4. 결과 리포트 생성 및 실패 케이스 출력
"""
import asyncio
import sys
from pathlib import Path

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

from google_drive_reader import GoogleDriveReader
from test_case_manager import TestCaseManager  # ✨ 새로 추가
from openai_interpreter import OpenAITestCaseInterpreter
from playwright_executor import PlaywrightMCPExecutor
from report_generator import ReportGenerator
import config


async def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("QA 테스트 자동화 시스템 시작")
    print("=" * 60)
    
    try:
        # 1. Google Drive에서 테스트케이스 읽기
        print("\n[1단계] Google Drive에서 테스트케이스 읽는 중...")
        drive_reader = GoogleDriveReader()
        
        # 파일 ID 또는 폴더 ID 확인
        file_id = config.settings.GOOGLE_DRIVE_FILE_ID
        folder_id = config.settings.GOOGLE_DRIVE_FOLDER_ID
        
        if not file_id and not folder_id:
            print("오류: Google Drive 파일 ID 또는 폴더 ID를 설정해야 합니다.")
            print("config.py 또는 .env 파일에서 GOOGLE_DRIVE_FILE_ID 또는 GOOGLE_DRIVE_FOLDER_ID를 설정하세요.")
            return
        
        if file_id:
            test_cases = drive_reader.read_test_cases_from_file(file_id)
        else:
            # 폴더에서 첫 번째 파일 사용
            files = drive_reader.list_files_in_folder(folder_id)
            if not files:
                print("오류: 폴더에 파일이 없습니다.")
                return
            print(f"폴더에서 {len(files)}개의 파일을 찾았습니다.")
            test_cases = drive_reader.read_test_cases_from_file(files[0]['id'])
        
        print(f"✓ {len(test_cases)}개의 테스트케이스를 읽었습니다.")
        
        # 📋 데이터 구조 확인 (디버깅용)
        if test_cases:
            print("\n" + "=" * 60)
            print("📋 Google Sheets 데이터 샘플")
            print("=" * 60)
            first_case = test_cases[0]
            print(f"첫 번째 테스트케이스의 키 목록:")
            print(f"  {list(first_case.keys())[:10]}...")
            print(f"\n첫 번째 테스트케이스의 데이터 샘플:")
            for key, value in list(first_case.items())[:5]:
                value_str = str(value)[:50]
                print(f"  {key}: {value_str}...")
        
        # ✨ [1.5단계] 테스트케이스 자동 생성/보정
        print("\n[1.5단계] 테스트케이스 자동 처리...")
        print("=" * 60)
        
        test_manager = TestCaseManager()
        
        if not test_cases or len(test_cases) == 0:
            # 케이스가 없으면 자동 생성
            print("⚠️  테스트케이스가 없습니다. 자동 생성 모드로 전환...")
            feature_description = """
            Google 검색 기능 테스트:
            - Google 메인 페이지 접속 및 확인
            - 검색어 입력 및 입력 확인
            - 검색 실행 및 결과 페이지 이동 확인
            - Google 이미지 검색 페이지 접속
            - Google 뉴스 페이지 접속
            """
            test_cases = test_manager.process_test_cases(
                test_cases=None,
                feature_description=feature_description,
                count=5
            )
        else:
            # 케이스가 있으면 자동 보정
            test_cases = test_manager.process_test_cases(
                test_cases=test_cases
            )
        
        if not test_cases:
            print("경고: 처리할 테스트케이스가 없습니다.")
            return
        
        # 2. OpenAI API로 테스트케이스 해석 (배치 처리)
        print("\n" + "=" * 60)
        print("[2단계] OpenAI API로 테스트케이스 해석 중...")
        print("=" * 60)
        interpreter = OpenAITestCaseInterpreter()
        interpreted_cases = interpreter.interpret_test_cases(test_cases)
        
        interpreted_count = sum(1 for case in interpreted_cases if case.get("status") == "interpreted")
        print(f"\n✓ {interpreted_count}/{len(interpreted_cases)}개의 테스트케이스가 해석되었습니다.")
        
        # 해석 실패한 케이스 확인
        failed_interpretations = [
            case for case in interpreted_cases 
            if case.get("status") != "interpreted"
        ]
        
        if failed_interpretations:
            print(f"\n⚠️  {len(failed_interpretations)}개의 테스트케이스 해석 실패")
        
        # 해석 성공 케이스 구조 확인
        if interpreted_count > 0:
            print("\n" + "-" * 60)
            print("✅ 해석 성공 케이스 샘플:")
            print("-" * 60)
            for case in interpreted_cases:
                if case.get("status") == "interpreted":
                    print(f"  ID: {case.get('id')}")
                    print(f"  interpretation 존재: {case.get('interpretation') is not None}")
                    
                    interpretation = case.get('interpretation')
                    if interpretation:
                        print(f"  interpretation 타입: {type(interpretation)}")
                        if isinstance(interpretation, dict):
                            print(f"  interpretation 키: {list(interpretation.keys())}")
                    break
        
        # 해석 실패가 너무 많으면 경고
        if interpreted_count == 0:
            print("\n" + "=" * 60)
            print("❌ 모든 테스트케이스 해석 실패!")
            print("=" * 60)
            return
        
        # 3. Playwright로 테스트 실행
        print("\n" + "=" * 60)
        print("[3단계] Playwright로 테스트 실행 중...")
        print("=" * 60)
        executor = PlaywrightMCPExecutor()
        test_results = await executor.execute_test_cases(interpreted_cases)
        
        # 결과 요약
        passed_count = sum(1 for r in test_results if r.get("status") == "passed")
        failed_count = sum(1 for r in test_results if r.get("status") == "failed")
        skipped_count = sum(1 for r in test_results if r.get("status") == "skipped")
        error_count = sum(1 for r in test_results if r.get("status") == "error")
        
        print(f"\n테스트 실행 완료:")
        print(f"  - 성공: {passed_count}")
        print(f"  - 실패: {failed_count}")
        print(f"  - 스킵: {skipped_count}")
        print(f"  - 오류: {error_count}")
        
        # 4. 결과 리포트 생성
        print("\n" + "=" * 60)
        print("[4단계] 결과 리포트 생성 중...")
        print("=" * 60)
        
        # 리포트 생성 전 데이터 유효성 검사
        valid_results = []
        for result in test_results:
            if result.get('interpretation') is None:
                result['interpretation'] = {
                    'purpose': 'Unknown',
                    'steps': [],
                    'expected': 'Unknown'
                }
            valid_results.append(result)
        
        report_generator = ReportGenerator()
        report_path = report_generator.generate_report(valid_results)
        print(f"✓ 리포트가 생성되었습니다: {report_path}")
        
        # 5. 실패/미수행 케이스 출력
        print("\n" + "=" * 60)
        print("[5단계] 실패 및 미수행 케이스 확인...")
        print("=" * 60)
        failed_cases = report_generator.get_failed_cases(valid_results)
        
        if failed_cases:
            print(f"\n⚠️  {len(failed_cases)}개의 케이스가 실패하거나 미수행되었습니다:")
            print("-" * 60)
            
            for i, case in enumerate(failed_cases, 1):
                status = case.get("status", "unknown")
                test_case = case.get("test_case", {})
                original = test_case.get("original", {})
                title = original.get("제목") or f"케이스 {i}"
                error = case.get("error", "")
                
                print(f"\n{i}. [{status.upper()}] {title}")
                if error:
                    print(f"   오류: {error}")
                
                # 실패한 단계 정보
                steps_failed = case.get("steps_failed", [])
                if steps_failed:
                    print(f"   실패한 단계:")
                    for step in steps_failed:
                        print(f"     - {step.get('action', '')}: {step.get('error', '')}")
            
            print("\n" + "=" * 60)
            print("이 케이스들은 QA 팀의 후속 검토가 필요합니다.")
            print("=" * 60)
        else:
            print("\n🎉 모든 테스트케이스가 성공적으로 실행되었습니다!")
        
        print(f"\n📊 상세 리포트: {report_path}")
        print("\n" + "=" * 60)
        print("QA 테스트 자동화 시스템 종료")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")
        print("\n상세 오류 정보:")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())