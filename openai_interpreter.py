"""
OpenAI API를 사용한 테스트케이스 해석 (배치 처리 최적화)
"""
from typing import List, Dict, Any
from openai import OpenAI
import config
import json


class OpenAITestCaseInterpreter:
    """OpenAI를 사용한 테스트케이스 해석 클래스"""
    
    def __init__(self):
        self.client = OpenAI(api_key=config.settings.OPENAI_API_KEY)
        self.model = config.settings.OPENAI_MODEL
        self.max_tokens = config.settings.OPENAI_MAX_TOKENS
    
    def interpret_test_cases(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        테스트케이스 배치 해석 (한 번의 API 호출로 모든 테스트 처리)
        
        Args:
            test_cases: 원본 테스트케이스 리스트
            
        Returns:
            해석된 테스트케이스 리스트
        """
        if not test_cases:
            return []
        
        total = len(test_cases)
        print(f"배치 해석 시작: {total}개 테스트케이스")
        
        try:
            # 배치 프롬프트 생성
            prompt = self._create_batch_prompt(test_cases)
            
            # 단일 API 호출로 모든 테스트 해석
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens * 2,
                temperature=0.3
            )
            
            # 응답 파싱
            response_text = response.choices[0].message.content
            interpretations = self._parse_batch_response(response_text, test_cases)
            
            # 결과 매칭
            results = []
            for i, test_case in enumerate(test_cases):
                if i < len(interpretations) and interpretations[i]:
                    results.append({
                        **test_case,
                        "interpretation": interpretations[i],
                        "status": "interpreted"
                    })
                else:
                    results.append({
                        **test_case,
                        "interpretation": None,
                        "status": "interpretation_failed",
                        "error": "배치 해석 중 파싱 실패"
                    })
            
            success_count = sum(1 for r in results if r.get("status") == "interpreted")
            print(f"✓ 배치 해석 완료: {success_count}/{total}개 성공")
            
            return results
            
        except Exception as e:
            print(f"❌ 배치 해석 실패: {str(e)}")
            print(f"⚠️  개별 해석 모드로 전환...")
            return self._interpret_individually(test_cases)
    
    def _create_batch_prompt(self, test_cases: List[Dict[str, Any]]) -> str:
        """배치 처리를 위한 프롬프트 생성"""
        
        test_cases_json = []
        for i, tc in enumerate(test_cases, 1):
            original = tc.get("original", tc)
            test_cases_json.append({
                "index": i,
                "id": original.get("시나리오 ID", f"TC_{i}"),
                "title": original.get("제목", ""),
                "precondition": original.get("Pre-condition", ""),
                "test_step": original.get("Test step", ""),
                "expected_result": original.get("Expected Result", ""),
                "link": original.get("Link", "")
            })
        
        prompt = f"""다음 {len(test_cases)}개의 테스트케이스를 분석하여 Playwright 자동화 스크립트로 변환해주세요.

# 테스트케이스 목록
```json
{json.dumps(test_cases_json, ensure_ascii=False, indent=2)}
```

# 요구사항
각 테스트케이스를 다음 JSON 형식으로 변환하세요:
```json
[
  {{
    "index": 1,
    "purpose": "테스트 목적 간단 요약",
    "prerequisites": ["사전조건1", "사전조건2"],
    "steps": [
      {{
        "action": "navigate|click|fill|press|wait|assert_url|assert_text",
        "target": "CSS선택자 또는 URL",
        "value": "입력값 (fill인 경우) 또는 키 이름 (press인 경우)"
      }}
    ],
    "verification": "예상 결과",
    "url": "테스트 시작 URL (있으면)"
  }},
  ...
]
```

# 액션 가이드
- **navigate**: URL로 이동 (target: URL)
- **click**: 요소 클릭 (target: CSS 선택자)
- **fill**: 입력 필드에 값 입력 (target: CSS 선택자, value: 입력값)
- **press**: 키보드 입력 (value: "Enter", "Tab", "Escape" 등)
- **wait**: 대기 (value: 밀리초)
- **assert_url**: URL 검증 (target: 포함되어야 할 문자열)
- **assert_text**: 텍스트 검증 (target: 찾을 텍스트)

# 중요 규칙
1. CSS 선택자는 구체적으로 (예: `input[name='q']`, `textarea[name='q']`)
2. press 액션의 value는 반드시 키 이름만 (예: "Enter", "Tab")
3. Google 검색창은 `textarea[name='q']` 사용
4. 응답은 JSON 배열만 출력 (추가 설명 없이)

응답:"""
        
        return prompt
    
    def _parse_batch_response(self, response_text: str, test_cases: List[Dict]) -> List[Dict]:
        """배치 응답 파싱"""
        try:
            # JSON 추출 (```json ... ``` 제거)
            json_text = response_text.strip()
            if "```json" in json_text:
                json_text = json_text.split("```json")[1].split("```")[0].strip()
            elif "```" in json_text:
                json_text = json_text.split("```")[1].split("```")[0].strip()
            
            # JSON 파싱
            interpretations_list = json.loads(json_text)
            
            # index로 정렬
            interpretations_list.sort(key=lambda x: x.get("index", 0))
            
            return interpretations_list
            
        except Exception as e:
            print(f"⚠️  배치 응답 파싱 오류: {str(e)}")
            print(f"응답 내용:\n{response_text[:500]}...")
            return []
    
    def _interpret_individually(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """개별 해석 (Fallback)"""
        results = []
        total = len(test_cases)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"개별 해석 중: {i}/{total}")
            
            try:
                interpretation = self._interpret_single(test_case)
                results.append({
                    **test_case,
                    "interpretation": interpretation,
                    "status": "interpreted"
                })
            except Exception as e:
                print(f"  ❌ 해석 실패: {str(e)}")
                results.append({
                    **test_case,
                    "interpretation": None,
                    "status": "interpretation_failed",
                    "error": str(e)
                })
        
        return results
    
    def _interpret_single(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """단일 테스트케이스 해석"""
        original = test_case.get("original", test_case)
        
        prompt = f"""다음 테스트케이스를 Playwright 자동화 스크립트로 변환해주세요:

제목: {original.get("제목", "")}
사전조건: {original.get("Pre-condition", "")}
테스트 단계: {original.get("Test step", "")}
예상 결과: {original.get("Expected Result", "")}
URL: {original.get("Link", "")}

JSON 형식으로만 응답:
{{
  "purpose": "테스트 목적",
  "prerequisites": ["사전조건"],
  "steps": [
    {{"action": "navigate", "target": "URL", "value": ""}},
    {{"action": "fill", "target": "textarea[name='q']", "value": "검색어"}},
    {{"action": "press", "target": "", "value": "Enter"}}
  ],
  "verification": "예상 결과",
  "url": "시작 URL"
}}"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": prompt}
            ],
            max_tokens=self.max_tokens,
            temperature=0.3
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # JSON 추출
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        return json.loads(response_text)
    
    def _get_system_prompt(self) -> str:
        """시스템 프롬프트"""
        return """당신은 QA 테스트 자동화 전문가입니다. 
테스트케이스를 Playwright 브라우저 자동화 스크립트로 변환하는 것이 목표입니다.
정확한 CSS 선택자와 액션을 사용하여 JSON 형식으로만 응답하세요."""