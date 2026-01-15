"""
유틸리티 함수 모듈
"""
from typing import Dict, Any
import json


def format_test_case_for_display(test_case: Dict[str, Any]) -> str:
    """테스트케이스를 읽기 쉬운 형식으로 포맷팅"""
    title = test_case.get("제목") or test_case.get("title") or test_case.get("테스트케이스", "제목 없음")
    purpose = test_case.get("목적") or test_case.get("purpose", "")
    
    formatted = f"제목: {title}\n"
    if purpose:
        formatted += f"목적: {purpose}\n"
    
    return formatted


def validate_test_case(test_case: Dict[str, Any]) -> bool:
    """테스트케이스 유효성 검사"""
    if not test_case:
        return False
    
    # 최소한 제목이나 목적이 있어야 함
    has_title = bool(test_case.get("제목") or test_case.get("title") or test_case.get("테스트케이스"))
    has_purpose = bool(test_case.get("목적") or test_case.get("purpose") or test_case.get("단계"))
    
    return has_title or has_purpose


def sanitize_filename(filename: str) -> str:
    """파일명에서 사용할 수 없는 문자 제거"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def parse_playwright_action(action: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Playwright 액션을 표준화된 형식으로 파싱
    
    Args:
        action: 액션 타입 (goto, click, fill, etc.)
        params: 액션 파라미터
    
    Returns:
        표준화된 액션 딕셔너리
    """
    standardized = {
        "action": action,
        "target": params.get("target", ""),
        "value": params.get("value", ""),
        "options": params.get("options", {})
    }
    
    # 액션별 특수 처리
    if action == "goto":
        standardized["url"] = params.get("url") or params.get("target", "")
    elif action == "fill":
        standardized["text"] = params.get("value") or params.get("text", "")
    elif action == "select":
        standardized["value"] = params.get("value") or params.get("option", "")
    
    return standardized

