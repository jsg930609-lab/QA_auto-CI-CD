"""
QA 자동화 시스템 설정 파일
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional
from pydantic import Field


class Settings(BaseSettings):
    # Google Drive 설정
    GOOGLE_DRIVE_CREDENTIALS_FILE: str = Field(default="credentials.json")
    GOOGLE_DRIVE_TOKEN_FILE: str = Field(default="token.json")
    GOOGLE_DRIVE_FILE_ID: str = Field(default="")
    GOOGLE_DRIVE_FOLDER_ID: str = Field(default="")
    
    # Google Sheets 설정
    GOOGLE_SHEETS_NAME: str = Field(default="Sheet1")
    GOOGLE_SHEETS_START_ROW: int = Field(default=12)
    
    # OpenAI 설정 (호환성을 위해 둘 다 정의)
    OPENAI_API_KEY: str = Field(default="")
    OPENAI_MODEL: str = Field(default="gpt-4o")
    OPENAI_MAX_TOKENS: int = Field(default=2000)  # ✅ 추가
    OPENAI_MAX_COMPLETION_TOKENS: int = Field(default=2000)  # ✅ 추가 (호환성)
    
    # Playwright MCP 설정
    PLAYWRIGHT_MCP_SERVER_URL: str = Field(default="http://localhost:3000")
    PLAYWRIGHT_BROWSER: str = Field(default="chromium")
    
    # 테스트 설정
    TEST_TIMEOUT: int = Field(default=30000)
    SCREENSHOT_ON_FAILURE: bool = Field(default=True)
    SCREENSHOT_DIR: str = Field(default="screenshots")
    
    # 리포트 설정
    REPORT_DIR: str = Field(default="reports")
    REPORT_FORMAT: str = Field(default="html")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # ✅ 추가: 추가 필드 무시

settings = Settings()

# 디렉토리 생성
Path(settings.SCREENSHOT_DIR).mkdir(exist_ok=True)
Path(settings.REPORT_DIR).mkdir(exist_ok=True)