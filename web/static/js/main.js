// ============================================
// 전역 변수
// ============================================
let allTestCases = [];
let updateInterval = null;

// ============================================
// 초기화
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM 로드 완료');
    initializeApp();
});

function initializeApp() {
    console.log('앱 초기화 시작');
    
    // 탭 전환
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            switchTab(e.target.dataset.tab);
        });
    });
    
    // 새로고침
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', refreshData);
        console.log('새로고침 버튼 이벤트 등록');
    }
    
    // 테스트 실행
    const runTestBtn = document.getElementById('runTestBtn');
    if (runTestBtn) {
        runTestBtn.addEventListener('click', runTests);
        console.log('테스트 실행 버튼 이벤트 등록');
    }
    
    // GitHub Actions 버튼
    const runGithubBtn = document.getElementById('runGithubBtn');
    if (runGithubBtn) {
        runGithubBtn.addEventListener('click', () => {
            console.log('GitHub Actions 버튼 클릭됨');
            showGithubModal();
        });
        console.log('GitHub Actions 버튼 이벤트 등록 완료');
    } else {
        console.error('GitHub Actions 버튼을 찾을 수 없습니다!');
    }
    
    // GitHub Actions 탭 내 트리거 버튼
    const triggerGithubBtn = document.getElementById('triggerGithubBtn');
    if (triggerGithubBtn) {
        triggerGithubBtn.addEventListener('click', triggerGithubActionsFromTab);
    }
    
    // 검색
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', filterTestCases);
    }
    
    // 필터
    const filterStatus = document.getElementById('filterStatus');
    if (filterStatus) {
        filterStatus.addEventListener('change', filterTestCases);
    }
    
    // 모달 닫기
    const modalClose = document.querySelector('.modal-close');
    if (modalClose) {
        modalClose.addEventListener('click', closeModal);
    }
    
    // 모달 외부 클릭 시 닫기
    const modal = document.getElementById('modal');
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal();
            }
        });
    }
    
    // 초기 데이터 로드
    refreshData();
    
    console.log('앱 초기화 완료');
}

// ============================================
// 데이터 로드
// ============================================
async function refreshData() {
    console.log('데이터 새로고침');
    try {
        await Promise.all([
            loadTestCases(),
            loadStats(),
            loadHistory(),
            checkTestStatus()
        ]);
    } catch (error) {
        console.error('데이터 새로고침 오류:', error);
    }
}

async function loadTestCases() {
    try {
        console.log('테스트 케이스 로드 중...');
        const response = await fetch('/api/test-cases');
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        console.log('테스트 케이스 로드 완료:', data.length);
        
        allTestCases = data;
        renderTestCases(data);
    } catch (error) {
        console.error('테스트 케이스 로드 실패:', error);
        const container = document.getElementById('testCasesList');
        if (container) {
            container.innerHTML = '<p class="empty-state">테스트 케이스를 불러올 수 없습니다.</p>';
        }
    }
}

async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const stats = await response.json();
        
        document.getElementById('totalTests').textContent = stats.total || 0;
        document.getElementById('passedTests').textContent = stats.passed || 0;
        document.getElementById('failedTests').textContent = stats.failed || 0;
        document.getElementById('skippedTests').textContent = stats.skipped || 0;
        
        const successRate = stats.total > 0 ? ((stats.passed / stats.total) * 100).toFixed(1) : 0;
        document.getElementById('successRate').textContent = `${successRate}%`;
    } catch (error) {
        console.error('통계 로드 실패:', error);
    }
}

async function loadHistory() {
    try {
        const response = await fetch('/api/history');
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const history = await response.json();
        renderHistory(history);
    } catch (error) {
        console.error('히스토리 로드 실패:', error);
    }
}

async function checkTestStatus() {
    try {
        const response = await fetch('/api/test-status');
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const status = await response.json();
        
        if (status.running) {
            showProgress(status);
            if (!updateInterval) {
                updateInterval = setInterval(checkTestStatus, 1000);
            }
        } else {
            hideProgress();
            if (updateInterval) {
                clearInterval(updateInterval);
                updateInterval = null;
            }
        }
    } catch (error) {
        console.error('상태 확인 실패:', error);
    }
}

// ============================================
// UI 렌더링
// ============================================
function renderTestCases(testCases) {
    const container = document.getElementById('testCasesList');
    
    if (!container) {
        console.error('testCasesList 컨테이너를 찾을 수 없습니다');
        return;
    }
    
    if (!testCases || testCases.length === 0) {
        container.innerHTML = '<p class="empty-state">테스트 케이스가 없습니다.</p>';
        return;
    }
    
    container.innerHTML = testCases.map((tc, index) => {
        const statusClass = tc.status === 'PASS' ? 'status-pass' : 
                           tc.status === 'FAIL' ? 'status-fail' : 'status-new';
        const statusEmoji = tc.status === 'PASS' ? '✅' : 
                           tc.status === 'FAIL' ? '❌' : '🆕';
        
        return `
            <div class="test-case-item" onclick="showTestDetail(${index})">
                <div class="test-case-header">
                    <span class="test-case-id">#${tc.id || index + 1}</span>
                    <span class="status-badge ${statusClass}">
                        ${statusEmoji} ${tc.status || 'NEW'}
                    </span>
                </div>
                <div class="test-case-title">${tc.title || '제목 없음'}</div>
            </div>
        `;
    }).join('');
}

function renderHistory(history) {
    const container = document.getElementById('historyList');
    
    if (!container) {
        console.error('historyList 컨테이너를 찾을 수 없습니다');
        return;
    }
    
    if (!history || history.length === 0) {
        container.innerHTML = '<p class="empty-state">실행 히스토리가 없습니다.</p>';
        return;
    }
    
    container.innerHTML = history.map(item => {
        const date = new Date(item.timestamp);
        const successRate = item.total > 0 ? 
            ((item.passed / item.total) * 100).toFixed(1) : 0;
        
        return `
            <div class="history-item">
                <div class="history-header">
                    <span class="history-date">${date.toLocaleString('ko-KR')}</span>
                    <span class="history-stats">
                        ✅ ${item.passed} / ❌ ${item.failed} / ⏭️ ${item.skipped}
                    </span>
                </div>
                <div class="history-bar">
                    <div class="history-bar-fill" style="width: ${successRate}%"></div>
                </div>
                <div class="history-footer">
                    <span>성공률: ${successRate}%</span>
                    ${item.report_path ? 
                        `<a href="${item.report_path}" target="_blank" class="btn btn-sm btn-secondary">리포트 보기</a>` 
                        : ''}
                </div>
            </div>
        `;
    }).join('');
}

function showProgress(status) {
    const section = document.getElementById('progressSection');
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    const currentTest = document.getElementById('currentTest');
    
    if (section) section.style.display = 'block';
    if (progressFill) progressFill.style.width = `${status.progress}%`;
    if (progressText) progressText.textContent = `${Math.round(status.progress * status.total / 100)}/${status.total}`;
    if (currentTest) currentTest.textContent = status.current_test || '실행 중...';
}

function hideProgress() {
    const section = document.getElementById('progressSection');
    if (section) section.style.display = 'none';
}

// ============================================
// 테스트 실행
// ============================================
async function runTests() {
    const btn = document.getElementById('runTestBtn');
    if (!btn) return;
    
    btn.disabled = true;
    btn.textContent = '⏳ 실행 중...';
    
    try {
        const response = await fetch('/api/run-tests', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            updateInterval = setInterval(checkTestStatus, 1000);
        } else {
            alert('테스트 실행 실패');
        }
    } catch (error) {
        console.error('테스트 실행 오류:', error);
        alert('테스트 실행 중 오류가 발생했습니다.');
    } finally {
        btn.disabled = false;
        btn.textContent = '▶️ 로컬 테스트 실행';
    }
}

// ============================================
// GitHub Actions 모달
// ============================================
function showGithubModal() {
    console.log('GitHub Actions 모달 표시');
    
    const modalBody = `
        <div class="github-modal-content">
            <p style="margin-bottom: 20px; color: #4a5568;">
                GitHub Actions 워크플로우를 실행합니다.
            </p>
            
            <div class="form-group">
                <label>환경:</label>
                <select id="modalGhEnvironment" class="input">
                    <option value="production">Production</option>
                    <option value="staging">Staging</option>
                    <option value="development">Development</option>
                </select>
            </div>
            
            <div class="form-group">
                <label>테스트 스위트:</label>
                <input type="text" id="modalGhTestSuite" class="input" 
                       value="all" placeholder="all">
            </div>
            
            <div class="form-group">
                <label>브라우저:</label>
                <select id="modalGhBrowser" class="input">
                    <option value="chromium">Chromium</option>
                    <option value="firefox">Firefox</option>
                    <option value="webkit">WebKit</option>
                </select>
            </div>
            
            <div style="margin-top: 24px; display: flex; gap: 12px;">
                <button id="modalTriggerBtn" class="btn btn-primary" style="flex: 1;">
                    🚀 실행
                </button>
                <button id="modalCancelBtn" class="btn btn-secondary" style="flex: 1;">
                    취소
                </button>
            </div>
        </div>
    `;
    
    showModal('GitHub Actions 실행', modalBody);
    
    // 모달 내 버튼에 이벤트 리스너 추가
    setTimeout(() => {
        const triggerBtn = document.getElementById('modalTriggerBtn');
        const cancelBtn = document.getElementById('modalCancelBtn');
        
        if (triggerBtn) {
            triggerBtn.addEventListener('click', triggerGithubActionsFromModal);
        }
        
        if (cancelBtn) {
            cancelBtn.addEventListener('click', closeModal);
        }
    }, 100);
}

async function triggerGithubActionsFromModal() {
    console.log('GitHub Actions 트리거 시작');
    
    const environment = document.getElementById('modalGhEnvironment')?.value || 'production';
    const testSuite = document.getElementById('modalGhTestSuite')?.value || 'all';
    const browser = document.getElementById('modalGhBrowser')?.value || 'chromium';
    
    console.log('선택된 옵션:', { environment, testSuite, browser });
    
    closeModal();
    
    const originalTitle = document.title;
    document.title = '⏳ GitHub Actions 트리거 중...';
    
    try {
        const response = await fetch('/api/trigger-github-actions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                environment: environment,
                test_suite: testSuite,
                browser: browser
            })
        });
        
        const data = await response.json();
        console.log('API 응답:', data);
        
        if (response.ok) {
            const successBody = `
                <div style="text-align: center; padding: 20px;">
                    <div style="font-size: 48px; margin-bottom: 16px;">✅</div>
                    <p style="font-size: 18px; font-weight: 600; margin-bottom: 12px;">
                        ${data.message}
                    </p>
                    <p style="color: #718096; margin-bottom: 24px;">
                        GitHub Actions 페이지에서 실행 상태를 확인하세요.
                    </p>
                    <div style="display: flex; gap: 12px; justify-content: center;">
                        <button id="openGithubBtn" class="btn btn-primary">
                            🔗 GitHub Actions 열기
                        </button>
                        <button id="closeSuccessBtn" class="btn btn-secondary">
                            닫기
                        </button>
                    </div>
                </div>
            `;
            showModal('실행 완료', successBody);
            
            setTimeout(() => {
                const openBtn = document.getElementById('openGithubBtn');
                const closeBtn = document.getElementById('closeSuccessBtn');
                
                if (openBtn && data.url) {
                    openBtn.addEventListener('click', () => {
                        window.open(data.url, '_blank');
                        closeModal();
                    });
                }
                
                if (closeBtn) {
                    closeBtn.addEventListener('click', closeModal);
                }
            }, 100);
            
        } else {
            showErrorModal(data.error || '알 수 없는 오류가 발생했습니다.');
        }
    } catch (error) {
        console.error('GitHub Actions 트리거 오류:', error);
        showErrorModal(error.message);
    } finally {
        document.title = originalTitle;
    }
}

function showErrorModal(message) {
    const errorBody = `
        <div style="text-align: center; padding: 20px;">
            <div style="font-size: 48px; margin-bottom: 16px;">❌</div>
            <p style="font-size: 18px; font-weight: 600; margin-bottom: 12px; color: #e53e3e;">
                오류 발생
            </p>
            <p style="color: #718096; margin-bottom: 24px;">
                ${message}
            </p>
            <button id="closeErrorBtn" class="btn btn-secondary">
                닫기
            </button>
        </div>
    `;
    showModal('오류', errorBody);
    
    setTimeout(() => {
        const closeBtn = document.getElementById('closeErrorBtn');
        if (closeBtn) {
            closeBtn.addEventListener('click', closeModal);
        }
    }, 100);
}

// ============================================
// GitHub Actions 탭
// ============================================
async function triggerGithubActionsFromTab() {
    const btn = document.getElementById('triggerGithubBtn');
    if (!btn) return;
    
    const originalText = btn.textContent;
    btn.disabled = true;
    btn.textContent = '⏳ 트리거 중...';
    
    try {
        const environment = document.getElementById('ghEnvironment')?.value || 'production';
        const browser = document.getElementById('ghBrowser')?.value || 'chromium';
        
        const response = await fetch('/api/trigger-github-actions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                environment: environment,
                browser: browser
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert(`✅ ${data.message}\n\nGitHub Actions 페이지에서 확인하세요.`);
            
            await loadGithubActionsStatus();
            
            if (data.url) {
                window.open(data.url, '_blank');
            }
        } else {
            alert(`❌ 오류: ${data.error}`);
        }
    } catch (error) {
        console.error('GitHub Actions 트리거 오류:', error);
        alert('트리거 중 오류가 발생했습니다.');
    } finally {
        btn.disabled = false;
        btn.textContent = originalText;
    }
}

async function loadGithubActionsStatus() {
    try {
        const response = await fetch('/api/github-actions-status');
        const runs = await response.json();
        
        renderGithubRuns(runs);
    } catch (error) {
        console.error('GitHub Actions 상태 로드 실패:', error);
    }
}

function renderGithubRuns(runs) {
    const container = document.getElementById('githubRunsList');
    
    if (!container) return;
    
    if (!runs || runs.length === 0) {
        container.innerHTML = '<p class="empty-state">실행된 워크플로우가 없습니다.</p>';
        return;
    }
    
    container.innerHTML = runs.map(run => {
        const date = new Date(run.created_at);
        const statusClass = run.conclusion === 'success' ? 'success' : 
                           run.conclusion === 'failure' ? 'failure' : '';
        
        return `
            <div class="github-run-item">
                <div>
                    <div style="font-weight: 600; margin-bottom: 4px;">${run.name}</div>
                    <div style="font-size: 12px; color: #718096;">
                        ${date.toLocaleString('ko-KR')}
                    </div>
                </div>
                <div style="display: flex; gap: 12px; align-items: center;">
                    <span class="run-status ${run.status} ${statusClass}">
                        ${run.status === 'completed' ? run.conclusion : run.status}
                    </span>
                    <a href="${run.html_url}" target="_blank" class="btn btn-secondary btn-sm">
                        보기
                    </a>
                </div>
            </div>
        `;
    }).join('');
}

// ============================================
// 모달
// ============================================
function showModal(title, body) {
    console.log('모달 표시:', title);
    const modal = document.getElementById('modal');
    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');
    
    if (modal && modalTitle && modalBody) {
        modalTitle.textContent = title;
        modalBody.innerHTML = body;
        modal.style.display = 'flex';  // ✨ 'flex'로 변경
        // 또는
        modal.classList.add('active');  // ✨ 클래스 방식
    }
}

function closeModal() {
    console.log('모달 닫기');
    const modal = document.getElementById('modal');
    if (modal) {
        modal.style.display = 'none';
        modal.classList.remove('active');  // ✨ 클래스 제거
    }
}

// ============================================
// 기타
// ============================================
function showTestDetail(index) {
    const testCase = allTestCases[index];
    if (!testCase) return;
    
    const body = `
        <div class="test-detail">
            <div class="detail-section">
                <div class="detail-row">
                    <strong>시나리오 ID:</strong>
                    <span>${testCase.id || 'N/A'}</span>
                </div>
                
                <div class="detail-row">
                    <strong>대분류:</strong>
                    <span>${testCase.category || 'N/A'}</span>
                </div>
                
                <div class="detail-row">
                    <strong>소분류:</strong>
                    <span>${testCase.subcategory || 'N/A'}</span>
                </div>
                
                <div class="detail-row">
                    <strong>제목:</strong>
                    <span>${testCase.title || 'N/A'}</span>
                </div>
                
                <div class="detail-row">
                    <strong>상태:</strong>
                    <span class="status-badge ${testCase.status === 'PASS' ? 'status-pass' : testCase.status === 'FAIL' ? 'status-fail' : 'status-new'}">
                        ${testCase.status === 'PASS' ? '✅' : testCase.status === 'FAIL' ? '❌' : '🆕'} ${testCase.status || 'NEW'}
                    </span>
                </div>
            </div>
            
            ${testCase.url ? `
                <div class="detail-section">
                    <strong>🔗 URL:</strong>
                    <a href="${testCase.url}" target="_blank" class="detail-link">${testCase.url}</a>
                </div>
            ` : ''}
            
            ${testCase.precondition ? `
                <div class="detail-section">
                    <strong>⚙️ Pre-condition:</strong>
                    <p>${testCase.precondition}</p>
                </div>
            ` : ''}
            
            ${testCase.steps && (Array.isArray(testCase.steps) ? testCase.steps.length > 0 : testCase.steps) ? `
                <div class="detail-section">
                    <strong>📝 테스트 단계:</strong>
                    ${Array.isArray(testCase.steps) 
                        ? `<ol class="detail-steps">
                            ${testCase.steps.map(step => `<li>${step}</li>`).join('')}
                           </ol>`
                        : `<p>${testCase.steps}</p>`
                    }
                </div>
            ` : ''}
            
            ${testCase.expected ? `
                <div class="detail-section">
                    <strong>✓ 예상 결과:</strong>
                    <p>${testCase.expected}</p>
                </div>
            ` : ''}
        </div>
    `;
    
    showModal(`테스트 케이스 상세`, body);
}

function filterTestCases() {
    const searchText = document.getElementById('searchInput')?.value.toLowerCase() || '';
    const statusFilter = document.getElementById('filterStatus')?.value || '';
    
    const filtered = allTestCases.filter(tc => {
        const matchesSearch = !searchText || 
            (tc.title && tc.title.toLowerCase().includes(searchText)) ||
            (tc.id && tc.id.toString().includes(searchText));
        
        const matchesStatus = !statusFilter || tc.status === statusFilter;
        
        return matchesSearch && matchesStatus;
    });
    
    renderTestCases(filtered);
}

function switchTab(tabName) {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.tab === tabName) {
            btn.classList.add('active');
        }
    });
    
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    const tabMap = {
        'testCases': 'testCasesTab',
        'history': 'historyTab',
        // 'reports': 'reportsTab',  ← 삭제
        'github': 'githubTab'
    };
    
    const targetTab = document.getElementById(tabMap[tabName]);
    if (targetTab) {
        targetTab.classList.add('active');
    }
    
    // 리포트 탭 로드 제거
    if (tabName === 'github') {
        loadGithubActionsStatus();
    }
}

console.log('main.js 로드 완료');