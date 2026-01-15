// ============================================
// 전역 변수
// ============================================
let allTestCases = [];
let allHistory = [];

// ============================================
// 초기화
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    console.log('페이지 로드 완료');
    
    // 탭 전환 이벤트
    setupTabs();
    
    // 초기 데이터 로드
    loadTestCases();
    loadHistory();
    loadGithubRuns();
    
    // 검색 및 필터 이벤트
    const searchInput = document.getElementById('searchInput');
    const filterStatus = document.getElementById('filterStatus');
    
    if (searchInput) {
        searchInput.addEventListener('input', filterTestCases);
    }
    
    if (filterStatus) {
        filterStatus.addEventListener('change', filterTestCases);
    }
    
    // 모달 닫기 이벤트
    const modal = document.getElementById('modal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeModal();
            }
        });
    }
});

// ============================================
// 탭 관리
// ============================================
function setupTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabName = this.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
}

function switchTab(tabName) {
    console.log('탭 전환:', tabName);
    
    // 모든 탭 버튼 비활성화
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // 모든 탭 컨텐츠 숨김
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // 선택된 탭 활성화
    const selectedButton = document.querySelector(`[data-tab="${tabName}"]`);
    const selectedContent = document.getElementById(`${tabName}Tab`);
    
    if (selectedButton) selectedButton.classList.add('active');
    if (selectedContent) selectedContent.classList.add('active');
    
    // 탭별 데이터 로드
    if (tabName === 'testCases') {
        loadTestCases();
    } else if (tabName === 'history') {
        loadHistory();
    } else if (tabName === 'github') {
        loadGithubRuns();
    }
}

// ============================================
// 테스트 케이스
// ============================================
async function loadTestCases() {
    try {
        console.log('테스트 케이스 로드 시작');
        
        const response = await fetch('/api/test-cases');
        const data = await response.json();
        
        console.log('테스트 케이스 데이터:', data);
        
        if (data.success) {
            allTestCases = data.testCases;
            renderTestCases(allTestCases);
            updateStats(data.stats);
        } else {
            console.error('테스트 케이스 로드 실패:', data.error);
            document.getElementById('testCasesList').innerHTML = 
                '<p class="empty-state">⚠️ 테스트 케이스를 불러오는데 실패했습니다.</p>';
        }
    } catch (error) {
        console.error('테스트 케이스 로드 오류:', error);
        document.getElementById('testCasesList').innerHTML = 
            '<p class="empty-state">⚠️ 서버 연결 오류</p>';
    }
}

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
                    <span class="test-case-id">#${tc.id || 'TC_' + (index + 1)}</span>
                    <span class="status-badge ${statusClass}">
                        ${statusEmoji} ${tc.status || 'NEW'}
                    </span>
                </div>
                <div class="test-case-title">${tc.title || '제목 없음'}</div>
            </div>
        `;
    }).join('');
}

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

function updateStats(stats) {
    if (!stats) return;
    
    const elements = {
        totalTests: stats.total || 0,
        passedTests: stats.passed || 0,
        failedTests: stats.failed || 0,
        newTests: stats.new || 0,
        successRate: `${stats.success_rate || 0}%`
    };
    
    Object.keys(elements).forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = elements[id];
        }
    });
}

function filterTestCases() {
    const searchTerm = document.getElementById('searchInput')?.value.toLowerCase() || '';
    const statusFilter = document.getElementById('filterStatus')?.value || 'all';
    
    let filtered = allTestCases;
    
    // 상태 필터
    if (statusFilter !== 'all') {
        filtered = filtered.filter(tc => tc.status === statusFilter);
    }
    
    // 검색어 필터
    if (searchTerm) {
        filtered = filtered.filter(tc => 
            (tc.title && tc.title.toLowerCase().includes(searchTerm)) ||
            (tc.id && tc.id.toLowerCase().includes(searchTerm)) ||
            (tc.category && tc.category.toLowerCase().includes(searchTerm))
        );
    }
    
    renderTestCases(filtered);
}

// ============================================
// 히스토리
// ============================================
async function loadHistory() {
    try {
        console.log('히스토리 로드 시작');
        
        const response = await fetch('/api/history');
        const data = await response.json();
        
        console.log('히스토리 데이터:', data);
        
        if (data.success) {
            allHistory = data.history;
            renderHistory(allHistory);
        } else {
            console.error('히스토리 로드 실패:', data.error);
            const container = document.getElementById('historyList');
            if (container) {
                container.innerHTML = '<p class="empty-state">⚠️ 히스토리를 불러오는데 실패했습니다.</p>';
            }
        }
    } catch (error) {
        console.error('히스토리 로드 오류:', error);
        const container = document.getElementById('historyList');
        if (container) {
            container.innerHTML = '<p class="empty-state">⚠️ 서버 연결 오류</p>';
        }
    }
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

    container.innerHTML = history.map((item, index) => {
        const passRate = item.total > 0 ? Math.round((item.passed / item.total) * 100) : 0;
        
        // 날짜 포맷팅
        const date = item.date || item.timestamp || new Date().toISOString();
        const formattedDate = formatHistoryDate(date);
        
        return `
            <div class="history-item">
                <div class="history-header">
                    <span class="history-date">📅 ${formattedDate}</span>
                    ${item.report_path ? 
                        `<button class="btn-report" onclick="showReportModal('${item.report_path}', ${index})">
                            📊 리포트 보기
                        </button>` 
                        : ''
                    }
                </div>
                <div class="history-stats">
                    ✅ ${item.passed} / ❌ ${item.failed} / ⏭️ ${item.skipped || 0} / ⏱️ ${item.duration || 'N/A'}
                </div>
                <div class="history-bar">
                    <div class="history-bar-fill" style="width: ${passRate}%"></div>
                </div>
                <div class="history-footer">
                    <span>전체: ${item.total}</span>
                    <span>성공률: ${passRate}%</span>
                </div>
            </div>
        `;
    }).join('');
}

// 날짜 포맷 헬퍼 함수
function formatHistoryDate(dateString) {
    try {
        const date = new Date(dateString);
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        const seconds = String(date.getSeconds()).padStart(2, '0');
        
        return `${year}. ${month}. ${day}. 오후 ${hours}:${minutes}:${seconds}`;
    } catch (e) {
        return dateString;
    }
}

// ============================================
// GitHub Actions
// ============================================
async function triggerGithubAction() {
    const environment = document.getElementById('githubEnvironment')?.value;
    const browser = document.getElementById('githubBrowser')?.value;
    
    if (!environment || !browser) {
        showModal('❌ 오류', '<p>환경과 브라우저를 선택해주세요.</p>');
        return;
    }
    
    try {
        console.log('GitHub Actions 트리거:', { environment, browser });
        
        const response = await fetch('/api/github/trigger', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                environment: environment,
                browser: browser
            })
        });
        
        console.log('Response status:', response.status);
        console.log('Response headers:', response.headers);
        
        // Content-Type 확인
        const contentType = response.headers.get('content-type');
        console.log('Content-Type:', contentType);
        
        if (!contentType || !contentType.includes('application/json')) {
            const text = await response.text();
            console.error('Non-JSON response:', text);
            showModal('❌ 오류', `<p>서버에서 올바른 응답을 받지 못했습니다.</p><pre>${text.substring(0, 200)}</pre>`);
            return;
        }
        
        const data = await response.json();
        console.log('Response data:', data);
        
        if (data.success) {
            const body = `
                <p>✅ ${data.message}</p>
                ${data.run_url ? `<p><a href="${data.run_url}" target="_blank" class="detail-link">실행 상태 확인 →</a></p>` : ''}
            `;
            showModal('✅ 성공', body);
            
            // 실행 히스토리 새로고침
            setTimeout(() => {
                loadGithubRuns();
            }, 2000);
        } else {
            const errorDetail = data.detail ? `<pre style="background: #f7fafc; padding: 12px; border-radius: 8px; overflow-x: auto; font-size: 12px;">${JSON.stringify(data.detail, null, 2)}</pre>` : '';
            showModal('❌ 오류 발생', `<p>${data.error}</p>${errorDetail}`);
        }
        
    } catch (error) {
        console.error('GitHub Actions 트리거 오류:', error);
        showModal('❌ 오류 발생', `<p>요청 처리 중 오류가 발생했습니다.</p><p>${error.message}</p>`);
    }
}

async function loadGithubRuns() {
    try {
        console.log('GitHub 실행 히스토리 로드 시작');
        
        const response = await fetch('/api/github/runs');
        
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const text = await response.text();
            console.error('Non-JSON response:', text);
            const container = document.getElementById('githubRunsList');
            if (container) {
                container.innerHTML = '<p class="empty-state">⚠️ 서버 응답 오류</p>';
            }
            return;
        }
        
        const data = await response.json();
        console.log('GitHub 실행 히스토리:', data);
        
        const container = document.getElementById('githubRunsList');
        if (!container) {
            console.error('githubRunsList 컨테이너를 찾을 수 없습니다');
            return;
        }
        
        if (!data.success || !data.runs || data.runs.length === 0) {
            container.innerHTML = '<p class="empty-state">실행 히스토리가 없습니다.</p>';
            return;
        }
        
        container.innerHTML = data.runs.map(run => {
            const statusClass = run.conclusion === 'success' ? 'success' : 
                              run.conclusion === 'failure' ? 'failure' : '';
            const statusText = run.status === 'completed' ? run.conclusion : run.status;
            const statusEmoji = run.conclusion === 'success' ? '✅' : 
                              run.conclusion === 'failure' ? '❌' : 
                              run.status === 'in_progress' ? '⏳' : '⏸️';
            
            return `
                <div class="github-run-item">
                    <div>
                        <div style="font-weight: 600; margin-bottom: 4px;">
                            ${run.name || 'Manual QA Test'}
                        </div>
                        <div style="font-size: 13px; color: #718096;">
                            ${new Date(run.created_at).toLocaleString('ko-KR')}
                        </div>
                    </div>
                    <div style="display: flex; gap: 8px; align-items: center;">
                        <span class="run-status ${run.status} ${statusClass}">
                            ${statusEmoji} ${statusText || 'unknown'}
                        </span>
                        <a href="${run.html_url}" target="_blank" class="btn btn-sm btn-secondary">
                            상세보기
                        </a>
                    </div>
                </div>
            `;
        }).join('');
        
    } catch (error) {
        console.error('GitHub 실행 히스토리 로드 오류:', error);
        const container = document.getElementById('githubRunsList');
        if (container) {
            container.innerHTML = '<p class="empty-state">⚠️ 실행 히스토리를 불러오는 중 오류가 발생했습니다.</p>';
        }
    }
}

function showGithubModal() {
    const body = `
        <div class="github-modal-content">
            <div class="form-group">
                <label for="modalEnvironment">테스트 환경</label>
                <select id="modalEnvironment" class="input">
                    <option value="production">Production</option>
                    <option value="staging">Staging</option>
                    <option value="development">Development</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="modalBrowser">브라우저</label>
                <select id="modalBrowser" class="input">
                    <option value="chromium">Chromium</option>
                    <option value="firefox">Firefox</option>
                    <option value="webkit">WebKit</option>
                </select>
            </div>
            
            <button class="btn btn-github" onclick="executeGithubAction()" style="width: 100%; margin-top: 16px;">
                🚀 실행
            </button>
        </div>
    `;
    
    showModal('🚀 GitHub Actions 실행', body);
}

async function executeGithubAction() {
    const environment = document.getElementById('modalEnvironment')?.value;
    const browser = document.getElementById('modalBrowser')?.value;
    
    closeModal();
    
    if (!environment || !browser) {
        showModal('❌ 오류', '<p>환경과 브라우저를 선택해주세요.</p>');
        return;
    }
    
    try {
        console.log('GitHub Actions 트리거:', { environment, browser });
        
        const response = await fetch('/api/github/trigger', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                environment: environment,
                browser: browser
            })
        });
        
        const contentType = response.headers.get('content-type');
        
        if (!contentType || !contentType.includes('application/json')) {
            const text = await response.text();
            console.error('Non-JSON response:', text);
            showModal('❌ 오류', `<p>서버에서 올바른 응답을 받지 못했습니다.</p>`);
            return;
        }
        
        const data = await response.json();
        console.log('Response data:', data);
        
        if (data.success) {
            const body = `
                <p>✅ ${data.message}</p>
                ${data.run_url ? `<p><a href="${data.run_url}" target="_blank" class="detail-link">실행 상태 확인 →</a></p>` : ''}
            `;
            showModal('✅ 성공', body);
            
            setTimeout(() => {
                loadGithubRuns();
            }, 2000);
        } else {
            const errorDetail = data.detail ? `<pre style="background: #f7fafc; padding: 12px; border-radius: 8px; overflow-x: auto; font-size: 12px;">${JSON.stringify(data.detail, null, 2)}</pre>` : '';
            showModal('❌ 오류 발생', `<p>${data.error}</p>${errorDetail}`);
        }
        
    } catch (error) {
        console.error('GitHub Actions 트리거 오류:', error);
        showModal('❌ 오류 발생', `<p>요청 처리 중 오류가 발생했습니다.</p><p>${error.message}</p>`);
    }
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
        modal.style.display = 'flex';  // flex로 중앙 정렬
    }
}

function closeModal() {
    console.log('모달 닫기');
    const modal = document.getElementById('modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// ============================================
// 테스트 실행
// ============================================
async function runAllTests() {
    try {
        const response = await fetch('/api/run-tests', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ type: 'all' })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showModal('✅ 테스트 시작', `<p>${data.message}</p><p>실행 ID: ${data.run_id}</p>`);
            
            // 히스토리 새로고침
            setTimeout(() => {
                loadHistory();
            }, 1000);
        } else {
            showModal('❌ 오류', `<p>${data.error}</p>`);
        }
    } catch (error) {
        console.error('테스트 실행 오류:', error);
        showModal('❌ 오류', `<p>테스트 실행 중 오류가 발생했습니다.</p><p>${error.message}</p>`);
    }
}

async function refreshData() {
    try {
        console.log('데이터 새로고침 시작');
        
        await Promise.all([
            loadTestCases(),
            loadHistory(),
            loadGithubRuns()
        ]);
        
        showModal('✅ 새로고침 완료', '<p>모든 데이터가 업데이트되었습니다.</p>');
        
        setTimeout(() => {
            closeModal();
        }, 1500);
        
    } catch (error) {
        console.error('데이터 새로고침 오류:', error);
        showModal('❌ 오류', `<p>데이터 새로고침 중 오류가 발생했습니다.</p>`);
    }
}

function showReportModal(reportPath, historyIndex) {
    if (!reportPath) {
        showModal('❌ 오류', '<p>리포트를 찾을 수 없습니다.</p>');
        return;
    }
    
    // 모달 HTML 생성 (통계 제거, iframe만 표시)
    const modalHTML = `
        <div class="report-modal-overlay" onclick="closeReportModal()">
            <div class="report-modal-content" onclick="event.stopPropagation()">
                <div class="report-modal-header">
                    <h2>📊 QA 테스트 리포트</h2>
                    <button class="modal-close-btn" onclick="closeReportModal()">×</button>
                </div>
                
                <div class="report-modal-body">
                    <div class="report-iframe-container">
                        <iframe src="${reportPath}" class="report-iframe"></iframe>
                    </div>
                </div>
                
                <div class="report-modal-footer">
                    <button class="btn-secondary" onclick="closeReportModal()">닫기</button>
                    <a href="${reportPath}" target="_blank" class="btn-primary">새 탭에서 열기</a>
                </div>
            </div>
        </div>
    `;
    
    // 기존 모달 제거 후 새로 추가
    closeReportModal();
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // ESC 키로 닫기
    document.addEventListener('keydown', handleEscKey);
}

function closeReportModal() {
    const modal = document.querySelector('.report-modal-overlay');
    if (modal) {
        modal.remove();
    }
    document.removeEventListener('keydown', handleEscKey);
}

function handleEscKey(e) {
    if (e.key === 'Escape') {
        closeReportModal();
    }
}