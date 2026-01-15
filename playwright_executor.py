"""
Playwright Python을 직접 사용한 브라우저 테스트 실행 (최적화 및 개선)
"""
import asyncio
from typing import List, Dict, Any
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
import config
import time
import os
from pathlib import Path


class PlaywrightMCPExecutor:
    """Playwright를 사용한 테스트 실행 클래스"""
    
    def __init__(self):
        self.timeout = config.settings.TEST_TIMEOUT
        self.screenshot_on_failure = config.settings.SCREENSHOT_ON_FAILURE
        self.screenshot_dir = config.settings.SCREENSHOT_DIR
        self.browser = None
        self.context = None
        
        # 스크린샷 디렉토리 생성
        Path(self.screenshot_dir).mkdir(parents=True, exist_ok=True)
        
        print("✓ Playwright Executor 초기화 완료")
    
    async def execute_test_cases(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """테스트케이스 실행"""
        results = []
        total = len(test_cases)
        
        # Playwright 초기화
        async with async_playwright() as p:
            # 브라우저 실행
            self.browser = await p.chromium.launch(
                headless=False,
                args=['--start-maximized']
            )
            
            # 브라우저 컨텍스트 생성
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080}
            )
            
            print(f"\n✓ 브라우저 시작 완료")
            
            # 각 테스트 실행
            for i, test_case in enumerate(test_cases, 1):
                print(f"\n{'='*60}")
                print(f"테스트 실행 중: {i}/{total}")
                print(f"{'='*60}")
                
                # 해석되지 않은 케이스는 스킵
                if test_case.get("status") != "interpreted":
                    print(f"⏭️  테스트 스킵 (해석 실패)")
                    results.append({
                        "test_case": test_case,
                        "status": "skipped",
                        "error": "테스트케이스 해석 실패",
                        "interpretation": None
                    })
                    continue
                
                # 테스트 실행
                result = await self._execute_single_test(test_case)
                results.append(result)
                
                # 테스트 간 짧은 대기
                await asyncio.sleep(0.5)
            
            print(f"\n{'='*60}")
            print(f"모든 테스트 실행 완료")
            print(f"{'='*60}")
            
            await self.browser.close()
        
        return results
    
    async def _execute_single_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """단일 테스트케이스 실행"""
        interpretation = test_case.get("interpretation", {})
        steps = interpretation.get("steps", [])
        
        # 새 페이지 생성
        page = await self.context.new_page()
        
        result = {
            "test_case": test_case,
            "interpretation": interpretation,
            "status": "passed",
            "steps_executed": [],
            "steps_failed": [],
            "error": None,
            "duration": 0
        }
        
        start_time = time.time()
        
        try:
            original = test_case.get("original", {})
            test_id = original.get("시나리오 ID", test_case.get("id", "Unknown"))
            test_title = original.get("제목", "Unknown")
            purpose = interpretation.get("purpose", "Unknown")
            
            print(f"\n📋 테스트 ID: {test_id}")
            print(f"📝 제목: {test_title}")
            print(f"🎯 목적: {purpose}")
            print(f"📊 단계 수: {len(steps)}")
            print(f"\n{'─'*60}")
            
            # 각 단계 실행
            for step_idx, step in enumerate(steps, 1):
                action = step.get("action", "").lower()
                target = step.get("target", "")
                value = step.get("value", "")
                
                # 단계 설명 출력
                step_desc = self._format_step_description(action, target, value)
                print(f"\n[단계 {step_idx}/{len(steps)}] {step_desc}")
                
                try:
                    # 액션 실행
                    await self._execute_action(page, action, target, value)
                    
                    # 성공 기록
                    result["steps_executed"].append({
                        "action": action,
                        "target": target,
                        "value": value,
                        "status": "success"
                    })
                    
                    print(f"  ✅ 성공")
                    
                    # 각 단계 후 스마트 대기 (networkidle 제거로 속도 향상)
                    if action in ["navigate", "goto"]:
                        # 페이지 이동 후에만 약간 대기
                        await asyncio.sleep(0.5)
                    else:
                        # 다른 액션은 아주 짧게
                        await asyncio.sleep(0.2)
                    
                except Exception as step_error:
                    error_msg = str(step_error)
                    print(f"  ❌ 실패: {error_msg}")
                    
                    # 실패 기록
                    result["steps_failed"].append({
                        "action": action,
                        "target": target,
                        "value": value,
                        "error": error_msg
                    })
                    
                    # 스크린샷 촬영
                    if self.screenshot_on_failure:
                        screenshot_path = os.path.join(
                            self.screenshot_dir,
                            f"failed_{test_id}_step{step_idx}.png"
                        )
                        await page.screenshot(path=screenshot_path)
                        print(f"  📸 스크린샷 저장: {screenshot_path}")
                    
                    result["status"] = "failed"
                    result["error"] = f"Step {step_idx} failed: {error_msg}"
                    break
            
            # 모든 단계 성공 시
            if not result["steps_failed"]:
                result["status"] = "passed"
                print(f"\n{'─'*60}")
                print(f"✅ 테스트 성공!")
            else:
                print(f"\n{'─'*60}")
                print(f"❌ 테스트 실패 ({len(result['steps_failed'])}개 단계 실패)")
            
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            print(f"\n{'─'*60}")
            print(f"❌ 테스트 오류: {str(e)}")
        
        finally:
            result["duration"] = time.time() - start_time
            print(f"⏱️  실행 시간: {result['duration']:.2f}초")
            await page.close()
        
        return result
    
    def _format_step_description(self, action: str, target: str, value: str) -> str:
        """단계 설명 포맷팅"""
        if action == "navigate" or action == "goto":
            return f"🌐 페이지 이동: {target}"
        elif action == "click":
            return f"🖱️  클릭: {target}"
        elif action in ["fill", "type"]:
            return f"⌨️  입력: {target} = '{value}'"
        elif action == "press":
            return f"⌨️  키 입력: {value or target}"
        elif action == "wait":
            return f"⏳ 대기: {value}ms"
        elif action in ["assert_url", "verify_url"]:
            return f"✓ URL 확인: '{target}' 포함 여부"
        elif action in ["assert_text", "verify_text"]:
            return f"✓ 텍스트 확인: '{target}'"
        elif action == "assert":
            return f"✓ 검증: {target}"
        else:
            return f"{action}: {target}"
    
    async def _execute_action(self, page: Page, action: str, target: str, value: str):
        """액션 실행"""
        
        if action in ["navigate", "goto"]:
            # 페이지 이동
            await page.goto(target, timeout=self.timeout, wait_until='domcontentloaded')
        
        elif action == "click":
            # 클릭
            if target.startswith("//"):
                await page.locator(f"xpath={target}").click(timeout=self.timeout)
            elif target.startswith("text=") or target.startswith("'") or target.startswith('"'):
                text = target.replace("text=", "").strip("'\"")
                await page.get_by_text(text).click(timeout=self.timeout)
            else:
                await page.click(target, timeout=self.timeout)
        
        elif action in ["fill", "type"]:
            # 입력 - 여러 선택자 시도
            selectors_to_try = []
            
            if target.startswith("//"):
                selectors_to_try.append(f"xpath={target}")
            elif target.startswith("placeholder="):
                placeholder = target.replace("placeholder=", "").strip("'\"")
                selectors_to_try.append(f"placeholder={placeholder}")
            elif target.startswith("label="):
                label = target.replace("label=", "").strip("'\"")
                selectors_to_try.append(f"label={label}")
            else:
                # CSS 선택자 - input과 textarea 모두 시도
                selectors_to_try.append(target)
                if "input" in target:
                    selectors_to_try.append(target.replace("input", "textarea"))
                elif "textarea" in target:
                    selectors_to_try.append(target.replace("textarea", "input"))
            
            # 각 선택자 시도
            filled = False
            last_error = None
            for selector in selectors_to_try:
                try:
                    await page.fill(selector, value, timeout=5000)
                    filled = True
                    break
                except Exception as e:
                    last_error = e
                    continue
            
            if not filled:
                raise last_error or Exception(f"입력 요소를 찾을 수 없음: {target}")
        
        elif action == "press":
            # 키 입력
            key_to_press = value or target
            
            # 일반적인 키 이름 정규화
            key_mapping = {
                "enter": "Enter",
                "return": "Enter", 
                "tab": "Tab",
                "escape": "Escape",
                "esc": "Escape",
                "space": " ",
                "backspace": "Backspace",
                "delete": "Delete",
                "del": "Delete",
                "arrowup": "ArrowUp",
                "up": "ArrowUp",
                "arrowdown": "ArrowDown",
                "down": "ArrowDown",
                "arrowleft": "ArrowLeft",
                "left": "ArrowLeft",
                "arrowright": "ArrowRight",
                "right": "ArrowRight",
                "pageup": "PageUp",
                "pagedown": "PageDown",
                "home": "Home",
                "end": "End"
            }
            
            key_lower = key_to_press.lower().strip()
            
            # 매핑 테이블에서 찾기
            if key_lower in key_mapping:
                key_to_press = key_mapping[key_lower]
            # CSS 선택자가 잘못 전달된 경우 감지
            elif any(indicator in key_to_press for indicator in ["[", "]", "=", "'", '"', "name", "id", "class", "//", ".", "#"]):
                print(f"  ⚠️  키 이름 대신 선택자가 전달됨: {key_to_press}")
                print(f"  ℹ️  'Enter' 키로 대체")
                key_to_press = "Enter"
            # 너무 긴 문자열도 의심
            elif len(key_to_press) > 20:
                print(f"  ⚠️  비정상적으로 긴 키 이름: {key_to_press}")
                print(f"  ℹ️  'Enter' 키로 대체")
                key_to_press = "Enter"
            
            await page.keyboard.press(key_to_press)
        
        elif action == "wait":
            # 대기
            wait_time = int(value) if value else 1000
            await page.wait_for_timeout(wait_time)
        
        elif action == "assert":
            # assert 액션 - 유연하게 처리
            if "url" in target.lower() or target == "page.url":
                current_url = page.url
                check_value = value if value else "google.com"
                if check_value not in current_url:
                    raise AssertionError(f"URL에 '{check_value}'이 포함되지 않음. 현재 URL: {current_url}")
            elif "text" in target.lower():
                if value:
                    await self._assert_text_flexible(page, value)
            else:
                # 요소 존재 확인
                try:
                    await page.wait_for_selector(target, timeout=5000, state='visible')
                except:
                    raise AssertionError(f"요소를 찾을 수 없음: {target}")
        
        elif action in ["assert_url", "verify_url"]:
            # URL 확인
            current_url = page.url
            if target not in current_url:
                raise AssertionError(f"URL에 '{target}'이 포함되지 않음. 현재 URL: {current_url}")
        
        elif action in ["assert_text", "verify_text"]:
            # 텍스트 확인 - 개선된 버전
            await self._assert_text_flexible(page, target)
        
        elif action == "screenshot":
            # 스크린샷
            screenshot_path = os.path.join(
                self.screenshot_dir,
                f"screenshot_{int(time.time())}.png"
            )
            await page.screenshot(path=screenshot_path)
            print(f"  📸 스크린샷 저장: {screenshot_path}")
        
        elif action == "scroll":
            # 스크롤
            if value:
                await page.evaluate(f"window.scrollBy(0, {value})")
            else:
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        
        elif action == "hover":
            # 호버
            await page.hover(target, timeout=self.timeout)
        
        else:
            raise ValueError(f"지원하지 않는 액션: {action}")
    
    async def _assert_text_flexible(self, page: Page, target: str):
        """
        텍스트 확인 - 다양한 방법으로 유연하게 처리
        """
        found = False
        
        # 방법 1: 페이지 HTML에서 찾기
        try:
            content = await page.content()
            if target in content:
                found = True
                return
        except:
            pass
        
        # 방법 2: 실제 표시되는 텍스트에서 찾기
        if not found:
            try:
                text_content = await page.evaluate("document.body.innerText")
                if target in text_content:
                    found = True
                    return
            except:
                pass
        
        # 방법 3: 모든 텍스트 노드에서 찾기
        if not found:
            try:
                all_text = await page.evaluate("""
                    () => {
                        return Array.from(document.querySelectorAll('*'))
                            .map(el => el.textContent)
                            .join(' ');
                    }
                """)
                if target in all_text:
                    found = True
                    return
            except:
                pass
        
        # 방법 4: 입력 필드의 value 확인
        if not found:
            try:
                elements = await page.query_selector_all("input, textarea")
                for element in elements:
                    value = await element.get_attribute("value")
                    if value and target in value:
                        found = True
                        return
            except:
                pass
        
        # 모든 방법 실패
        if not found:
            raise AssertionError(f"페이지에 '{target}' 텍스트를 찾을 수 없음")