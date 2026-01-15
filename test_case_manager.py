"""
테스트케이스 자동 생성 및 보정 통합 관리
- 케이스가 없으면: 자연어 설명으로부터 자동 생성
- 케이스가 있으면: 독립성 확보를 위한 자동 보정
"""
from typing import List, Dict, Any, Optional
from openai import OpenAI
import config
import json


class TestCaseManager:
    """테스트케이스 자동 생성/보정 통합 클래스"""
    
    def __init__(self):
        self.client = OpenAI(api_key=config.settings.OPENAI_API_KEY)
        self.model = config.settings.OPENAI_MODEL
        self.max_tokens = config.settings.OPENAI_MAX_TOKENS
    
    def process_test_cases(
        self, 
        test_cases: Optional[List[Dict[str, Any]]] = None,
        feature_description: Optional[str] = None,
        count: int = 5
    ) -> List[Dict[str, Any]]:
        """
        테스트케이스 처리 (생성 또는 보정)
        
        Args:
            test_cases: 기존 테스트케이스 (있으면 보정, 없으면 생성)
            feature_description: 기능 설명 (생성 시 필요)
            count: 생성할 테스트케이스 수 (생성 시)
            
        Returns:
            처리된 테스트케이스 리스트
        """
        if test_cases and len(test_cases) > 0:
            # 케이스가 있으면 보정
            print("\n🔧 기존 테스트케이스 자동 보정 모드")
            return self.enhance_test_cases(test_cases)
        elif feature_description:
            # 케이스가 없고 설명이 있으면 생성
            print("\n✨ 테스트케이스 자동 생성 모드")
            return self.generate_test_cases(feature_description, count)
        else:
            print("\n⚠️  테스트케이스가 없고 기능 설명도 없습니다.")
            return []
    
    def generate_test_cases(self, feature_description: str, count: int = 5) -> List[Dict[str, Any]]:
        """
        자연어 설명으로부터 테스트케이스 자동 생성
        
        Args:
            feature_description: 테스트하려는 기능 설명
            count: 생성할 테스트케이스 수
            
        Returns:
            생성된 테스트케이스 리스트
        """
        print("=" * 60)
        print(f"생성할 테스트케이스 수: {count}개")
        print(f"기능 설명: {feature_description[:100]}...")
        print("=" * 60)
        
        prompt = f"""다음 기능에 대한 완전하고 독립적인 테스트케이스 {count}개를 생성해주세요:

기능 설명:
{feature_description}

# 요구사항
1. 각 테스트는 완전히 독립적으로 실행 가능해야 함
2. 모든 사전조건을 Test step에 포함
3. 구체적인 URL, 선택자, 입력값 명시
4. 검증 가능한 예상 결과 작성

# JSON 형식
[
  {{
    "scenario_id": "TEST_001",
    "category": "기능 대분류",
    "subcategory": "기능 소분류",
    "title": "테스트 제목",
    "precondition": "사전조건",
    "test_step": "1. https://example.com 접속\\n2. 입력창에 '테스트' 입력\\n3. 제출 버튼 클릭\\n4. 결과 확인",
    "expected_result": "성공 메시지 표시, URL에 'success' 포함",
    "link": "https://example.com"
  }}
]

응답:"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 QA 테스트 전문가입니다. 완전하고 독립적인 테스트케이스를 작성합니다."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens * 3,
                temperature=0.7  # 생성 시에는 약간 높은 temperature
            )
            
            response_text = response.choices[0].message.content
            generated_cases = self._parse_json_response(response_text)
            
            if not generated_cases:
                print("❌ 테스트케이스 생성 실패")
                return []
            
            # 표준 형식으로 변환
            test_cases = []
            for i, case_data in enumerate(generated_cases, 1):
                test_case = {
                    "id": f"GENERATED_{i}",
                    "row_number": i,
                    "original": {
                        "시나리오 ID": case_data.get("scenario_id", f"GENERATED_{i}"),
                        "대분류": case_data.get("category", "자동생성"),
                        "소분류": case_data.get("subcategory", ""),
                        "제목": case_data.get("title", f"테스트 {i}"),
                        "Pre-condition": case_data.get("precondition", ""),
                        "Test step": case_data.get("test_step", ""),
                        "Expected Result": case_data.get("expected_result", ""),
                        "Link": case_data.get("link", ""),
                        "작성자": "AI Auto-Generated",
                        "상태": "NEW"
                    }
                }
                test_case["original"]["original"] = test_case["original"].copy()
                test_cases.append(test_case)
            
            print(f"\n✓ {len(test_cases)}개의 테스트케이스가 생성되었습니다.")
            
            # 생성된 케이스 미리보기
            if test_cases:
                print("\n📋 생성된 테스트케이스 미리보기:")
                for i, tc in enumerate(test_cases[:3], 1):
                    original = tc["original"]
                    print(f"\n{i}. {original['제목']}")
                    print(f"   ID: {original['시나리오 ID']}")
                    steps = original['Test step'].split('\n') if original['Test step'] else []
                    print(f"   단계: {len(steps)}개")
                    if len(steps) > 0:
                        print(f"   첫 단계: {steps[0][:50]}...")
                
                if len(test_cases) > 3:
                    print(f"\n... 외 {len(test_cases) - 3}개")
            
            return test_cases
            
        except Exception as e:
            print(f"❌ 생성 실패: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def enhance_test_cases(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        기존 테스트케이스 자동 보정
        - 독립성 확보
        - 누락된 단계 추가
        - 검증 조건 명확화
        
        Args:
            test_cases: 원본 테스트케이스 리스트
            
        Returns:
            보정된 테스트케이스 리스트
        """
        if not test_cases:
            return []
        
        total = len(test_cases)
        print("=" * 60)
        print(f"보정할 테스트케이스 수: {total}개")
        print("=" * 60)
        
        try:
            # 원본 데이터 추출
            cases_data = []
            for i, tc in enumerate(test_cases, 1):
                original = tc.get("original", tc)
                cases_data.append({
                    "index": i,
                    "scenario_id": original.get("시나리오 ID", f"TC_{i}"),
                    "category": original.get("대분류", ""),
                    "subcategory": original.get("소분류", ""),
                    "title": original.get("제목", ""),
                    "precondition": original.get("Pre-condition", ""),
                    "test_step": original.get("Test step", ""),
                    "expected_result": original.get("Expected Result", ""),
                    "link": original.get("Link", "")
                })
            
            prompt = f"""다음 테스트케이스들을 분석하여 **완전히 독립적으로 실행 가능하도록** 보정해주세요:

# 원본 테스트케이스
```json
{json.dumps(cases_data, ensure_ascii=False, indent=2)}
```

# 보정 규칙
1. **독립성 확보**: 각 테스트는 다른 테스트 없이도 실행 가능해야 함
2. **사전조건 포함**: 필요한 페이지 접속, 로그인 등을 Test step 첫 부분에 추가
3. **구체적 단계**: URL, CSS 선택자, 입력값을 구체적으로 명시
4. **검증 명확화**: Expected Result를 검증 가능하게 작성
5. **URL 정확성**: 검증 조건이 실제 URL 패턴과 일치하는지 확인

# 보정 예시
원본:
- 제목: "검색어 입력"
- Test step: "검색창에 'test' 입력"

보정:
- 제목: "검색어 입력"
- Test step: "1. https://www.google.com 접속\\n2. 검색창(textarea[name='q'])에 'test' 입력\\n3. 검색창에 'test'가 입력되었는지 확인"

# 특별 주의사항
- Google 이미지 검색 URL: https://www.google.com/imghp → URL 검증 시 'imghp' 또는 'google.com' 확인
- Google 검색창 선택자: textarea[name='q'] 사용
- 검색 후 URL: 'search?q=' 패턴 확인

# 응답 형식 (JSON 배열)
[
  {{
    "index": 1,
    "scenario_id": "원본 ID 유지",
    "category": "원본 유지",
    "subcategory": "원본 유지",
    "title": "원본 제목 유지 또는 개선",
    "precondition": "원본 유지",
    "test_step": "보정된 단계 (독립적으로, 번호 포함)",
    "expected_result": "명확한 검증 조건",
    "link": "원본 유지 또는 개선",
    "changes": ["추가된 변경사항1", "추가된 변경사항2"]
  }}
]

응답:"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 QA 테스트 전문가입니다. 테스트케이스를 독립적이고 완전하게 만듭니다."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens * 3,
                temperature=0.3
            )
            
            response_text = response.choices[0].message.content
            enhanced_data = self._parse_json_response(response_text)
            
            if not enhanced_data:
                print("⚠️  보정 데이터 파싱 실패, 원본 사용")
                return test_cases
            
            # 원본에 보정 데이터 적용
            enhanced_cases = []
            for i, tc in enumerate(test_cases):
                if i < len(enhanced_data):
                    enhanced_info = enhanced_data[i]
                    
                    # 원본 복사
                    enhanced_tc = tc.copy()
                    original = enhanced_tc.get("original", {}).copy()
                    
                    # 보정된 값 적용
                    original["제목"] = enhanced_info.get("title", original.get("제목", ""))
                    original["Test step"] = enhanced_info.get("test_step", original.get("Test step", ""))
                    original["Expected Result"] = enhanced_info.get("expected_result", original.get("Expected Result", ""))
                    original["Link"] = enhanced_info.get("link", original.get("Link", ""))
                    
                    # 변경사항 기록
                    enhanced_tc["enhancement_changes"] = enhanced_info.get("changes", [])
                    enhanced_tc["original"] = original
                    
                    enhanced_cases.append(enhanced_tc)
                else:
                    enhanced_cases.append(tc)
            
            print(f"\n✓ {len(enhanced_cases)}개의 테스트케이스가 보정되었습니다.")
            
            # 변경 사항 요약
            self._print_changes_summary(test_cases, enhanced_cases)
            
            return enhanced_cases
            
        except Exception as e:
            print(f"❌ 보정 실패: {str(e)}")
            import traceback
            traceback.print_exc()
            print(f"⚠️  원본 테스트케이스를 사용합니다.")
            return test_cases
    
    def _parse_json_response(self, response_text: str) -> List[Dict]:
        """JSON 응답 파싱"""
        try:
            # JSON 추출
            json_text = response_text.strip()
            if "```json" in json_text:
                json_text = json_text.split("```json")[1].split("```")[0].strip()
            elif "```" in json_text:
                json_text = json_text.split("```")[1].split("```")[0].strip()
            
            # JSON 파싱
            data = json.loads(json_text)
            
            # 리스트가 아니면 리스트로 변환
            if not isinstance(data, list):
                data = [data]
            
            return data
            
        except Exception as e:
            print(f"⚠️  JSON 파싱 오류: {str(e)}")
            print(f"응답 내용:\n{response_text[:500]}...")
            return []
    
    def _print_changes_summary(self, original_cases: List[Dict], enhanced_cases: List[Dict]):
        """변경사항 요약 출력"""
        print("\n" + "=" * 60)
        print("📝 보정 변경사항 요약")
        print("=" * 60)
        
        has_changes = False
        for i, (orig, enhanced) in enumerate(zip(original_cases, enhanced_cases), 1):
            changes = enhanced.get("enhancement_changes", [])
            if changes:
                has_changes = True
                orig_title = orig.get("original", {}).get("제목", f"테스트 {i}")
                print(f"\n{i}. {orig_title}")
                for change in changes:
                    print(f"   • {change}")
        
        if not has_changes:
            print("\n변경사항 없음 (원본 테스트가 이미 완전함)")
        
        print("\n" + "=" * 60)