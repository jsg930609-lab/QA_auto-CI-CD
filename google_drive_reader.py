"""
Google Drive에서 테스트케이스를 읽어오는 모듈
"""
import os
import json
from typing import List, Dict, Optional, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import config


# Google Drive API 스코프
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']


class GoogleDriveReader:
    """Google Drive에서 테스트케이스를 읽어오는 클래스"""
    
    def __init__(self):
        self.service = None
        self.credentials = None
        self._authenticate()
    
    def _authenticate(self):
        """Google Drive API 인증"""
        creds = None
        
        # 기존 토큰 파일 확인
        if os.path.exists(config.settings.GOOGLE_DRIVE_TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(
                config.settings.GOOGLE_DRIVE_TOKEN_FILE, SCOPES
            )
        
        # 토큰이 없거나 만료된 경우 재인증
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(config.settings.GOOGLE_DRIVE_CREDENTIALS_FILE):
                    raise FileNotFoundError(
                        f"Google Drive 인증 파일을 찾을 수 없습니다: "
                        f"{config.settings.GOOGLE_DRIVE_CREDENTIALS_FILE}"
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    config.settings.GOOGLE_DRIVE_CREDENTIALS_FILE, SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # 토큰 저장
            with open(config.settings.GOOGLE_DRIVE_TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
        
        self.credentials = creds
        self.service = build('drive', 'v3', credentials=creds)
    
    def read_test_cases_from_file(self, file_id: Optional[str] = None) -> List[Dict]:
        """
        Google Drive 파일에서 테스트케이스 읽기
        
        Args:
            file_id: Google Drive 파일 ID (없으면 설정 파일의 값 사용)
        
        Returns:
            테스트케이스 리스트
        """
        file_id = file_id or config.settings.GOOGLE_DRIVE_FILE_ID
        if not file_id:
            raise ValueError("Google Drive 파일 ID가 설정되지 않았습니다.")
        
        try:
            # 파일 메타데이터 가져오기
            file_metadata = self.service.files().get(fileId=file_id).execute()
            mime_type = file_metadata.get('mimeType', '')
            file_name = file_metadata.get('name', 'Unknown')
            
            print(f"파일 이름: {file_name}")
            print(f"MIME 타입: {mime_type}")
            
            # 파일 내용 다운로드
            if 'spreadsheet' in mime_type:
                # Google Sheets인 경우
                return self._read_google_sheets(file_id)
            elif 'document' in mime_type:
                # Google Docs인 경우
                return self._read_google_docs(file_id)
            else:
                # 일반 파일 (CSV, JSON 등)
                return self._read_generic_file(file_id)
        
        except HttpError as error:
            raise Exception(f"Google Drive 파일 읽기 실패: {error}")
    
    def _read_google_sheets(self, file_id: str) -> List[Dict[str, Any]]:
        """Google Sheets에서 테스트케이스 읽기"""
        try:
            # Google Sheets API 사용
            sheets_service = build('sheets', 'v4', credentials=self.credentials)
            
            # 시트 이름과 시작 행 설정
            sheet_name = config.settings.GOOGLE_SHEETS_NAME
            start_row = config.settings.GOOGLE_SHEETS_START_ROW
            
            # 범위 지정: 'Sheet1!A12:Z' (A열부터 Z열까지, 12행부터 끝까지)
            range_name = f'{sheet_name}!A{start_row}:Z'
            
            print(f"읽기 범위: {range_name}")
            
            # 시트 데이터 읽기
            result = sheets_service.spreadsheets().values().get(
                spreadsheetId=file_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                print("경고: 지정된 범위에 데이터가 없습니다.")
                return []
            
            # 첫 번째 행을 헤더로 사용
            headers = values[0]
            print(f"헤더 ({len(headers)}개): {headers}")
            
            # 빈 헤더 제거 및 정리
            cleaned_headers = []
            for i, h in enumerate(headers):
                header = str(h).strip() if h else f"Column_{i+1}"
                cleaned_headers.append(header)
            
            # 나머지 행을 데이터로 변환
            test_cases = []
            for row_idx, row in enumerate(values[1:], start=start_row + 1):
                # 빈 행 건너뛰기
                if not row or not any(str(cell).strip() for cell in row):
                    continue
                
                # 행의 길이가 헤더보다 짧으면 빈 값으로 채우기
                while len(row) < len(cleaned_headers):
                    row.append('')
                
                # 딕셔너리로 변환
                test_case = {}
                for j, header in enumerate(cleaned_headers):
                    test_case[header] = str(row[j]).strip() if j < len(row) else ''
                
                # ID와 행 번호 추가 (시트의 실제 행 번호 사용)
                test_case['id'] = f"TC_{row_idx}"
                test_case['row_number'] = row_idx
                test_case['original'] = test_case.copy()  # 원본 데이터 보관
                
                test_cases.append(test_case)
            
            print(f"총 {len(test_cases)}개의 테스트케이스를 읽었습니다.")
            
            # 첫 번째 테스트케이스 샘플 출력
            if test_cases:
                print(f"\n첫 번째 테스트케이스 샘플 (ID: {test_cases[0].get('id')}):")
                for key, value in list(test_cases[0].items())[:5]:
                    value_str = str(value)[:50]
                    print(f"  {key}: {value_str}...")
            
            return test_cases
            
        except HttpError as error:
            print(f"Google Sheets 읽기 오류: {error}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Google Sheets 읽기 실패: {error}")
    
    def _read_google_docs(self, file_id: str) -> List[Dict]:
        """Google Docs에서 테스트케이스 읽기 (텍스트 파싱)"""
        try:
            docs_service = build('docs', 'v1', credentials=self.credentials)
            doc = docs_service.documents().get(documentId=file_id).execute()
            
            # 문서 내용 추출 및 파싱
            content = doc.get('body', {}).get('content', [])
            text_content = self._extract_text_from_docs(content)
            
            # 간단한 파싱 (실제로는 더 정교한 파싱 필요)
            return self._parse_text_to_test_cases(text_content)
        
        except HttpError as error:
            raise Exception(f"Google Docs 읽기 실패: {error}")
    
    def _extract_text_from_docs(self, content: List) -> str:
        """Google Docs 내용에서 텍스트 추출"""
        text_parts = []
        for element in content:
            if 'paragraph' in element:
                para = element['paragraph']
                for text_run in para.get('elements', []):
                    if 'textRun' in text_run:
                        text_parts.append(text_run['textRun'].get('content', ''))
        return ''.join(text_parts)
    
    def _parse_text_to_test_cases(self, text: str) -> List[Dict]:
        """텍스트를 테스트케이스로 파싱"""
        test_cases = []
        lines = text.split('\n')
        
        current_case = {}
        for line in lines:
            line = line.strip()
            if not line:
                if current_case:
                    test_cases.append(current_case)
                    current_case = {}
                continue
            
            if ':' in line:
                key, value = line.split(':', 1)
                current_case[key.strip()] = value.strip()
        
        if current_case:
            test_cases.append(current_case)
        
        return test_cases
    
    def _read_generic_file(self, file_id: str) -> List[Dict]:
        """일반 파일 (CSV, JSON 등) 읽기"""
        try:
            request = self.service.files().get_media(fileId=file_id)
            content = request.execute()
            
            # 파일 확장자에 따라 파싱
            file_metadata = self.service.files().get(fileId=file_id).execute()
            file_name = file_metadata.get('name', '')
            
            if file_name.endswith('.json'):
                return json.loads(content.decode('utf-8'))
            elif file_name.endswith('.csv'):
                import csv
                import io
                csv_content = io.StringIO(content.decode('utf-8'))
                reader = csv.DictReader(csv_content)
                return list(reader)
            else:
                # 기본적으로 텍스트로 파싱 시도
                return self._parse_text_to_test_cases(content.decode('utf-8'))
        
        except HttpError as error:
            raise Exception(f"파일 읽기 실패: {error}")
    
    def list_files_in_folder(self, folder_id: Optional[str] = None) -> List[Dict]:
        """
        폴더 내 파일 목록 가져오기
        
        Args:
            folder_id: Google Drive 폴더 ID
        
        Returns:
            파일 정보 리스트
        """
        folder_id = folder_id or config.settings.GOOGLE_DRIVE_FOLDER_ID
        if not folder_id:
            raise ValueError("Google Drive 폴더 ID가 설정되지 않았습니다.")
        
        try:
            query = f"'{folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                fields="files(id, name, mimeType)"
            ).execute()
            
            return results.get('files', [])
        
        except HttpError as error:
            raise Exception(f"폴더 목록 가져오기 실패: {error}")