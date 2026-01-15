"""
Google Drive에서 테스트케이스를 읽어오는 모듈
"""
import os
from typing import List, Dict, Optional, Any
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

load_dotenv()

# Google API 스코프
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets.readonly',
    'https://www.googleapis.com/auth/drive.readonly'
]


class GoogleDriveReader:
    """Google Drive/Sheets에서 테스트케이스를 읽어오는 클래스"""
    
    def __init__(self):
        """초기화 및 인증"""
        self.service = None
        self.sheets_service = None
        self.credentials = None
        self._authenticate()
    
    def _authenticate(self):
        """Google API 인증 (Service Account 방식)"""
        try:
            credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
            
            if not os.path.exists(credentials_file):
                raise FileNotFoundError(
                    f"Google 인증 파일을 찾을 수 없습니다: {credentials_file}"
                )
            
            # Service Account 인증
            self.credentials = Credentials.from_service_account_file(
                credentials_file,
                scopes=SCOPES
            )
            
            # Google Drive API 서비스
            self.service = build('drive', 'v3', credentials=self.credentials)
            
            # Google Sheets API 서비스
            self.sheets_service = build('sheets', 'v4', credentials=self.credentials)
            
            print("✅ Google API 인증 성공")
            
        except Exception as e:
            print(f"❌ Google API 인증 실패: {str(e)}")
            import traceback
            traceback.print_exc()
            self.service = None
            self.sheets_service = None
    
    def read_test_cases_from_file(self, file_id: Optional[str] = None) -> List[Dict]:
        """
        Google Drive 파일에서 테스트케이스 읽기
        
        Args:
            file_id: Google Drive 파일 ID
        
        Returns:
            테스트케이스 리스트
        """
        if not file_id:
            file_id = os.getenv('GOOGLE_DRIVE_FILE_ID')
        
        if not file_id:
            raise ValueError("Google Drive 파일 ID가 설정되지 않았습니다.")
        
        if not self.service:
            print("❌ Google API가 초기화되지 않았습니다.")
            return []
        
        try:
            # 파일 메타데이터 가져오기
            file_metadata = self.service.files().get(fileId=file_id).execute()
            mime_type = file_metadata.get('mimeType', '')
            file_name = file_metadata.get('name', 'Unknown')
            
            print(f"📄 파일 이름: {file_name}")
            print(f"📋 MIME 타입: {mime_type}")
            
            # Google Sheets인 경우
            if 'spreadsheet' in mime_type:
                return self._read_google_sheets(file_id)
            else:
                print(f"⚠️ 지원하지 않는 파일 형식: {mime_type}")
                return []
        
        except HttpError as error:
            print(f"❌ Google Drive 파일 읽기 실패: {error}")
            import traceback
            traceback.print_exc()
            return []
        except Exception as e:
            print(f"❌ 예상치 못한 오류: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def _read_google_sheets(self, file_id: str) -> List[Dict[str, Any]]:
        """Google Sheets에서 테스트케이스 읽기"""
        try:
            if not self.sheets_service:
                print("❌ Google Sheets 서비스가 초기화되지 않았습니다.")
                return []
            
            # 시트 이름과 시작 행 설정
            sheet_name = os.getenv('GOOGLE_SHEETS_NAME', 'Sheet1')
            start_row = int(os.getenv('GOOGLE_SHEETS_START_ROW', '12'))
            
            # 범위 지정
            range_name = f'{sheet_name}!A{start_row}:Z'
            
            print(f"📖 읽기 범위: {range_name}")
            
            # 시트 데이터 읽기
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=file_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                print("⚠️ 지정된 범위에 데이터가 없습니다.")
                return []
            
            print(f"✅ Google Sheets에서 {len(values)}개 행 읽기 성공")
            
            # 첫 번째 행을 헤더로 사용
            headers = values[0] if values else []
            print(f"📋 헤더 ({len(headers)}개): {headers[:5]}...")  # 처음 5개만 출력
            
            # 헤더 정리
            cleaned_headers = []
            for i, h in enumerate(headers):
                header = str(h).strip() if h else f"Column_{i+1}"
                cleaned_headers.append(header)
            
            # 데이터 행 파싱
            test_cases = []
            for row_idx, row in enumerate(values[1:], start=start_row + 1):
                # 빈 행 건너뛰기
                if not row or not any(str(cell).strip() for cell in row):
                    continue
                
                # 행 길이를 헤더와 맞추기
                while len(row) < len(cleaned_headers):
                    row.append('')
                
                # 딕셔너리로 변환
                test_case = {}
                for j, header in enumerate(cleaned_headers):
                    value = str(row[j]).strip() if j < len(row) else ''
                    test_case[header] = value
                
                # 기본 필드 매핑 (헤더 이름과 관계없이)
                # 컬럼 순서: A=ID, B=대분류, C=소분류, D=제목, E=URL, F=Pre-condition, G=단계, H=예상결과, I=상태
                if len(row) >= 1:
                    test_case['id'] = row[0] if row[0] else f"TC_{row_idx}"
                if len(row) >= 2:
                    test_case['category'] = row[1] if row[1] else ''
                if len(row) >= 3:
                    test_case['subcategory'] = row[2] if row[2] else ''
                if len(row) >= 4:
                    test_case['title'] = row[3] if row[3] else ''
                if len(row) >= 5:
                    test_case['url'] = row[4] if row[4] else ''
                if len(row) >= 6:
                    test_case['precondition'] = row[5] if row[5] else ''
                if len(row) >= 7:
                    steps_text = row[6] if row[6] else ''
                    # 줄바꿈으로 단계 구분
                    test_case['steps'] = [
                        s.strip() 
                        for s in steps_text.split('\n') 
                        if s.strip()
                    ]
                if len(row) >= 8:
                    test_case['expected'] = row[7] if row[7] else ''
                if len(row) >= 9:
                    status = row[8].strip().upper() if row[8] else 'NEW'
                    # 상태 정규화
                    if status in ['PASS', 'SUCCESS', '성공', '통과']:
                        status = 'PASS'
                    elif status in ['FAIL', 'FAILED', 'FAILURE', '실패']:
                        status = 'FAIL'
                    else:
                        status = 'NEW'
                    test_case['status'] = status
                else:
                    test_case['status'] = 'NEW'
                
                # 메타데이터
                test_case['row_number'] = row_idx
                
                test_cases.append(test_case)
            
            print(f"✅ {len(test_cases)}개 테스트케이스 파싱 완료")
            
            # 첫 번째 샘플 출력
            if test_cases:
                sample = test_cases[0]
                print(f"\n📝 첫 번째 테스트케이스 샘플:")
                print(f"  ID: {sample.get('id')}")
                print(f"  제목: {sample.get('title', '')[:50]}...")
                print(f"  상태: {sample.get('status')}")
            
            return test_cases
            
        except HttpError as error:
            print(f"❌ Google Sheets 읽기 오류: {error}")
            import traceback
            traceback.print_exc()
            return []
        except Exception as e:
            print(f"❌ 예상치 못한 오류: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def list_files_in_folder(self, folder_id: Optional[str] = None) -> List[Dict]:
        """
        폴더 내 파일 목록 가져오기
        
        Args:
            folder_id: Google Drive 폴더 ID
        
        Returns:
            파일 정보 리스트
        """
        if not folder_id:
            folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
        
        if not folder_id:
            raise ValueError("Google Drive 폴더 ID가 설정되지 않았습니다.")
        
        if not self.service:
            print("❌ Google Drive 서비스가 초기화되지 않았습니다.")
            return []
        
        try:
            query = f"'{folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                fields="files(id, name, mimeType)"
            ).execute()
            
            files = results.get('files', [])
            print(f"✅ 폴더에서 {len(files)}개 파일 발견")
            
            return files
        
        except HttpError as error:
            print(f"❌ 폴더 목록 가져오기 실패: {error}")
            return []