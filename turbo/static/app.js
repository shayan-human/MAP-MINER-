const formCard = document.getElementById('form-card');
const statusCard = document.getElementById('status-card');
const form = document.getElementById('scrape-form');
const backBtn = document.getElementById('back-btn');
const spinner = document.getElementById('spinner');
const progressBar = document.getElementById('progress-bar');
const statusText = document.getElementById('status-text');
const statusSub = document.getElementById('status-sub');
const resultsSummary = document.getElementById('results-summary');
const downloadActions = document.getElementById('download-actions');
const downloadUniqueBtn = document.getElementById('download-unique-btn');
const downloadAllBtn = document.getElementById('download-all-btn');
const statsTotal = document.getElementById('stats-total');
const statsDuplicates = document.getElementById('stats-duplicates');
const statsUnique = document.getElementById('stats-unique');
const countUnique = document.getElementById('count-unique');
const countTotal = document.getElementById('count-total');

// === Sequential Batch Elements ===
const bulkModeToggle = document.getElementById('bulk-mode-toggle');
const singleLocationInput = document.getElementById('single-location-input');
const bulkLocationInput = document.getElementById('bulk-location-input');
const bulkLocationsArea = document.getElementById('bulk-locations');
const locationInput = document.getElementById('location');
const batchProgressContainer = document.getElementById('batch-progress-container');
const batchProgressText = document.getElementById('batch-progress-text');
const batchProgressBar = document.getElementById('batch-progress-bar');

let isBulkMode = false;
let batchQueue = [];
let batchTotal = 0;
let batchCurrent = 0;

const resultsFilter = document.getElementById('results-filter');
const resultsPreviewBody = document.getElementById('results-preview-body');
let currentResults = { unique: [], duplicates: [] };
const filterRadios = document.getElementsByName('result-filter');

// === Page containers ===
const pages = {
    extractor: document.getElementById('page-extractor'),
    history: document.getElementById('page-history'),
    datasets: document.getElementById('page-datasets'),
    enricher: document.getElementById('page-enricher'),
    proxies: document.getElementById('page-proxies'),
    settings: document.getElementById('page-settings')
};

const notificationDot = document.querySelector('.notification-dot');

// === Navigation ===
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', () => {
        const page = item.dataset.page;
        switchPage(page);
    });
});

function switchPage(page) {
    // Update nav
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    const activeNav = document.querySelector(`.nav-item[data-page="${page}"]`);
    if (activeNav) activeNav.classList.add('active');

    // Update topbar
    const titles = { extractor: 'New Extraction Task', history: 'Extraction History', datasets: 'Datasets', enricher: 'Email Enricher', proxies: 'Proxy Manager', settings: 'Settings' };
    document.getElementById('topbar-title').textContent = titles[page] || 'Map Miner';

    // Show/hide pages
    Object.keys(pages).forEach(k => {
        if (pages[k]) pages[k].style.display = k === page ? 'block' : 'none';
    });

    // Handle wide layout for data-heavy pages
    const inner = document.querySelector('.content-inner');
    if (inner) {
        if (['history', 'datasets', 'proxies', 'enricher'].includes(page)) {
            inner.classList.add('wide');
        } else {
            inner.classList.remove('wide');
        }
    }

    // Load data for specific pages
    if (page === 'history') loadHistory();
    if (page === 'datasets') loadDatasets();
    if (page === 'proxies') loadProxies();
}

// === Concurrency Slider ===
const concurrencySlider = document.getElementById('concurrency');
const concurrencyValue = document.getElementById('concurrency-value');
function updateSlider() {
    const val = ((concurrencySlider.value - concurrencySlider.min) / (concurrencySlider.max - concurrencySlider.min)) * 100;
    concurrencySlider.style.setProperty('--val', val + '%');
    concurrencyValue.textContent = concurrencySlider.value + ' Threads';
}
concurrencySlider.addEventListener('input', updateSlider);
updateSlider();

// === Proxy Toggle ===
const advancedToggle = document.getElementById('advanced-toggle');
const proxyContent = document.getElementById('proxy-content');
advancedToggle.addEventListener('change', () => {
    proxyContent.classList.toggle('show', advancedToggle.checked);
});

// === Strict Mode Toggle - Extraction ===
const strictModeExtraction = document.getElementById('strict-mode-extraction');
const strictModeExtractionLabel = document.getElementById('strict-mode-extraction-label');
if (strictModeExtraction) {
    strictModeExtraction.addEventListener('change', function() {
        const slider = this.nextElementSibling;
        slider.classList.toggle('strict-active', this.checked);
        if (strictModeExtractionLabel) {
            strictModeExtractionLabel.style.color = this.checked ? '#dc3545' : '#6c757d';
        }
    });
}

// === Strict Mode Toggle - Enrichment ===
const strictModeEnrich = document.getElementById('strict-mode-enrich');
const strictModeEnrichLabel = document.getElementById('strict-mode-enrich-label');
if (strictModeEnrich) {
    strictModeEnrich.addEventListener('change', function() {
        const slider = this.nextElementSibling;
        slider.classList.toggle('strict-active', this.checked);
        if (strictModeEnrichLabel) {
            strictModeEnrichLabel.style.color = this.checked ? '#dc3545' : '#6c757d';
        }
    });
}

// === Bulk Mode Toggle ===
bulkModeToggle.addEventListener('change', () => {
    isBulkMode = bulkModeToggle.checked;
    singleLocationInput.style.display = isBulkMode ? 'none' : 'block';
    bulkLocationInput.style.display = isBulkMode ? 'block' : 'none';
    if (isBulkMode) {
        locationInput.removeAttribute('required');
        bulkLocationsArea.setAttribute('required', 'true');
    } else {
        locationInput.setAttribute('required', 'true');
        bulkLocationsArea.removeAttribute('required');
    }
});

// === Theme Toggle ===
const themeToggle = document.getElementById('theme-toggle');
const themeIcon = document.getElementById('theme-icon');
const sunPath = '<circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>';
const moonPath = '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>';
themeToggle.addEventListener('click', () => {
    document.body.classList.toggle('dark');
    const isDark = document.body.classList.contains('dark');
    themeIcon.innerHTML = isDark ? moonPath : sunPath;
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
});

// === Notifications ===
function showNotification() {
    if (notificationDot) notificationDot.classList.add('has-notification');
}

function hideNotification() {
    if (notificationDot) notificationDot.classList.remove('has-notification');
}

if (notificationDot) {
    notificationDot.addEventListener('click', hideNotification);
}
if (localStorage.getItem('theme') === 'light') {
    document.body.classList.remove('dark');
    themeIcon.innerHTML = sunPath;
}

// === Save Config ===
document.getElementById('save-config-btn').addEventListener('click', () => {
    const config = {
        niche: document.getElementById('niche').value,
        location: document.getElementById('location').value,
        max_results: document.getElementById('max_results').value,
        concurrency: concurrencySlider.value,
        proxies: document.getElementById('proxies').value,
        extract_all: document.getElementById('extract_all').checked
    };
    localStorage.setItem('mapMinerConfig', JSON.stringify(config));
    const btn = document.getElementById('save-config-btn');
    const original = btn.innerHTML;
    btn.innerHTML = '✓ Saved!';
    btn.style.borderColor = 'var(--accent-green)';
    btn.style.color = 'var(--accent-green)';
    setTimeout(() => { btn.innerHTML = original; btn.style.borderColor = ''; btn.style.color = ''; }, 1800);
});

// Restore config on load
const savedConfig = localStorage.getItem('mapMinerConfig');
if (savedConfig) {
    const c = JSON.parse(savedConfig);
    if (c.niche) document.getElementById('niche').value = c.niche;
    if (c.location) document.getElementById('location').value = c.location;
    if (c.max_results) document.getElementById('max_results').value = c.max_results;
    if (c.concurrency) { concurrencySlider.value = c.concurrency; updateSlider(); }
    if (c.proxies) { document.getElementById('proxies').value = c.proxies; advancedToggle.checked = true; proxyContent.classList.add('show'); }
    if (c.hasOwnProperty('extract_all')) { document.getElementById('extract_all').checked = c.extract_all; }
}

// === Proxy Verification ===
const verifyProxyBtn = document.getElementById('verify-proxy-btn');
const proxyInput = document.getElementById('proxies');
const proxyHint = document.getElementById('proxy-hint');
const proxyTypeExtraction = document.getElementById('proxy-type-extraction');

verifyProxyBtn.addEventListener('click', async () => {
    const proxyType = proxyTypeExtraction.value;
    const rawProxy = proxyInput.value.trim().split('\n')[0].trim(); // Take first proxy
    if (!rawProxy) {
        proxyHint.innerText = 'Please enter a proxy first';
        proxyHint.classList.add('proxy-hint-error');
        return;
    }

    // Apply protocol prefix if not already present
    const proxyVal = rawProxy.includes('://') ? rawProxy : proxyType + rawProxy;

    // Reset UI
    verifyProxyBtn.classList.add('loading');
    verifyProxyBtn.classList.remove('success', 'error');
    proxyHint.innerText = 'Testing connection...';
    proxyHint.classList.remove('proxy-hint-success', 'proxy-hint-error');

    try {
        const response = await fetch('/api/test-proxy', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ proxy: proxyVal })
        });
        const data = await response.json();

        verifyProxyBtn.classList.remove('loading');
        if (data.status === 'success') {
            verifyProxyBtn.classList.add('success');
            proxyHint.innerText = `Success! IP: ${data.ip}`;
            proxyHint.classList.add('proxy-hint-success');
        } else {
            verifyProxyBtn.classList.add('error');
            // Show message or detail (FastAPI) or raw data
            const errorMsg = data.message || data.detail || (typeof data === 'string' ? data : JSON.stringify(data));
            proxyHint.innerText = `Failed: ${errorMsg}`;
            proxyHint.classList.add('proxy-hint-error');
        }
    } catch (err) {
        verifyProxyBtn.classList.remove('loading');
        verifyProxyBtn.classList.add('error');
        proxyHint.innerText = `Request failed: ${err.message}`;
        proxyHint.classList.add('proxy-hint-error');
    }
});

// === Form Submit ===
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const niche = document.getElementById('niche').value;
    const maxResults = document.getElementById('max_results').value;
    const concurrency = concurrencySlider.value;
    const proxyType = document.getElementById('proxy-type-extraction').value;
    const rawProxies = document.getElementById('proxies').value;
    // Apply protocol prefix to each proxy line
    const proxies = rawProxies.split('\n').map(p => {
        p = p.trim();
        if (p && !p.includes('://')) {
            return proxyType + p;
        }
        return p;
    }).join('\n');
    const extractAll = document.getElementById('extract_all').checked;
    const emailLimit = extractAll ? 0 : 1;
    const strictMode = document.getElementById('strict-mode-extraction').checked;

    if (isBulkMode) {
        const rawLocations = bulkLocationsArea.value.split('\n').map(l => l.trim()).filter(l => l);
        if (rawLocations.length === 0) return alert('Please enter at least one location/ZIP code');
        
        batchQueue = rawLocations;
        batchTotal = rawLocations.length;
        batchCurrent = 0;
        
        formCard.style.display = 'none';
        statusCard.style.display = 'block';
        batchProgressContainer.style.display = 'block';
        
        processNextBatchItem(niche, maxResults, concurrency, proxies, emailLimit, strictMode);
    } else {
        const location = locationInput.value;
        if (!location) return alert('Please enter a location');
        
        const fd = new FormData();
        fd.append('niche', niche);
        fd.append('location', location);
        fd.append('max_results', maxResults);
        fd.append('concurrency', concurrency);
        fd.append('proxies', proxies);
        fd.append('email_limit', emailLimit);
        fd.append('strict_mode', strictMode);

        formCard.style.display = 'none';
        statusCard.style.display = 'block';
        batchProgressContainer.style.display = 'none';
        
        startSingleScrape(fd);
    }
});

async function startSingleScrape(formData) {
    statusText.innerText = 'Connecting to Engine...';
    statusSub.innerText = 'Launching extraction pipeline';
    if (spinner) spinner.style.display = 'inline-block';
    if (downloadActions) downloadActions.style.display = 'none';
    if (resultsSummary) resultsSummary.style.display = 'none';
    if (backBtn) backBtn.style.display = 'inline-block';
    if (progressBar) {
        progressBar.classList.add('indeterminate');
        progressBar.style.width = '40%';
    }

    try {
        const response = await fetch('/api/scrape', { method: 'POST', body: formData });
        const data = await response.json();
        pollStatus(data.job_id);
    } catch (err) {
        statusText.innerText = 'Error launching engine.';
        statusSub.innerText = 'Please check the server logs';
        spinner.style.display = 'none';
        progressBar.classList.remove('indeterminate');
    }
}

async function processNextBatchItem(niche, maxResults, concurrency, proxies, emailLimit, strictMode) {
    if (batchQueue.length === 0) {
        statusText.innerText = 'All Batches Complete';
        statusSub.innerText = `Processed ${batchTotal} locations sequentially.`;
        if (spinner) spinner.style.display = 'none';
        return;
    }

    const currentLocation = batchQueue.shift();
    batchCurrent++;
    
    // Update batch UI
    batchProgressText.innerText = `ZIP ${batchCurrent} of ${batchTotal}: ${currentLocation}`;
    batchProgressBar.style.width = `${(batchCurrent / batchTotal) * 100}%`;
    
    const fd = new FormData();
    fd.append('niche', niche);
    fd.append('location', currentLocation);
    fd.append('max_results', maxResults);
    fd.append('concurrency', concurrency);
    fd.append('proxies', proxies);
    fd.append('email_limit', emailLimit);
    fd.append('strict_mode', strictMode);

    statusText.innerText = `Initializing Batch: ${currentLocation}`;
    statusSub.innerText = `Sequential task ${batchCurrent}/${batchTotal}`;
    
    if (spinner) spinner.style.display = 'inline-block';
    if (progressBar) {
        progressBar.classList.add('indeterminate');
    }

    try {
        const response = await fetch('/api/scrape', { method: 'POST', body: fd });
        const data = await response.json();
        
        // Custom polling for batch mode
        const pollBatchStatus = () => {
            const intv = setInterval(async () => {
                try {
                    const res = await fetch(`/api/jobs/${data.job_id}`);
                    const statusData = await res.json();
                    
                    statusText.innerText = `[${currentLocation}] ${statusData.status}`;
                    
                    const enrichMatch = statusData.status.match(/\((\d+)\/(\d+)\)/);
                    if (enrichMatch) {
                        const currentL = parseInt(enrichMatch[1]);
                        const totalL = parseInt(enrichMatch[2]);
                        progressBar.classList.remove('indeterminate');
                        progressBar.style.width = Math.round((currentL / totalL) * 100) + '%';
                    }

                    if (statusData.status === 'Complete' || statusData.status.startsWith('Error') || statusData.status.startsWith('No')) {
                        clearInterval(intv);
                        // Move to next batch after a short delay
                        setTimeout(() => {
                            processNextBatchItem(niche, maxResults, concurrency, proxies, emailLimit, strictMode);
                        }, 2000);
                    }
                } catch (e) { /* retry */ }
            }, 1500);
        };
        pollBatchStatus();
        
    } catch (err) {
        statusText.innerText = `Batch Error: ${currentLocation}`;
        setTimeout(() => {
            processNextBatchItem(niche, maxResults, concurrency, proxies, emailLimit, strictMode);
        }, 3000);
    }
}

async function pollStatus(jobId) {
    const intv = setInterval(async () => {
        try {
            const res = await fetch(`/api/jobs/${jobId}`);
            const data = await res.json();
            statusText.innerText = data.status;
            const enrichMatch = data.status.match(/\((\d+)\/(\d+)\)/);
            if (enrichMatch) {
                const current = parseInt(enrichMatch[1]);
                const total = parseInt(enrichMatch[2]);
                const pct = Math.round((current / total) * 100);
                progressBar.classList.remove('indeterminate');
                progressBar.style.width = pct + '%';
                statusSub.innerText = `Processing lead ${current} of ${total}`;
            }
            if (data.status === 'Complete') {
                clearInterval(intv);
                if (spinner) spinner.style.display = 'none';
                if (progressBar) {
                    progressBar.classList.remove('indeterminate');
                    progressBar.style.width = '100%';
                }

                // Show statistics
                const totalLeads = data.total_found || data.result_count || 0;
                const withEmail = data.email_count || 0;
                const noEmail = totalLeads - withEmail;

                if (statsTotal) statsTotal.innerText = totalLeads || '?';
                const statsWithEmail = document.getElementById('stats-with-email');
                const statsNoEmail = document.getElementById('stats-no-email');
                if (statsWithEmail) statsWithEmail.innerText = withEmail;
                if (statsNoEmail) statsNoEmail.innerText = noEmail >= 0 ? noEmail : 0;
                if (statsDuplicates) statsDuplicates.innerText = data.duplicates_skipped || 0;
                if (resultsSummary) resultsSummary.style.display = 'block';

                const rc = data.result_count || '?';
                const ec = data.email_count || 0;
                statusSub.innerText = `Done! ${rc} leads extracted, ${ec} with emails.`;

                // Set download buttons
                if (countUnique) countUnique.innerText = data.unique_found || rc;
                if (countTotal) countTotal.innerText = data.total_found || rc;
                if (data.file_unique || data.file) {
                    if (downloadUniqueBtn) downloadUniqueBtn.href = `/api/download/${data.file_unique || data.file}`;
                    if (downloadUniqueBtn) downloadUniqueBtn.style.display = 'inline-flex';
                } else {
                    if (downloadUniqueBtn) downloadUniqueBtn.style.display = 'none';
                }

                if (data.file_all || data.file) {
                    if (downloadAllBtn) downloadAllBtn.href = `/api/download/${data.file_all || data.file}`;
                }
                if (downloadActions) downloadActions.style.display = 'flex';

                // Set results for preview
                currentResults.unique = data.results_unique || [];
                currentResults.duplicates = data.results_duplicates || [];
                renderPreview('all');
                if (resultsFilter) resultsFilter.style.display = 'block';

                if (backBtn) backBtn.style.display = 'inline-block';
                showNotification();
            } else if (data.status.startsWith('Error') || data.status.startsWith('No')) {
                clearInterval(intv);
                if (spinner) spinner.style.display = 'none';
                if (progressBar) {
                    progressBar.classList.remove('indeterminate');
                    progressBar.style.width = '0%';
                }
                statusSub.innerText = data.status || 'The extraction did not produce results.';
                if (backBtn) backBtn.style.display = 'inline-block';
            }
        } catch (err) { /* retry silently */ }
    }, 1500);
}

backBtn.addEventListener('click', () => {
    if (statusCard) statusCard.style.display = 'none';
    if (formCard) formCard.style.display = 'block';
    if (resultsFilter) resultsFilter.style.display = 'none';
    if (resultsSummary) resultsSummary.style.display = 'none';
    if (downloadActions) downloadActions.style.display = 'none';
    if (backBtn) backBtn.style.display = 'none';
});

// function renderPreview ... (existing)

function renderPreview(filter) {
    if (!resultsPreviewBody) return;
    resultsPreviewBody.innerHTML = '';
    let items = [];
    if (filter === 'all') {
        items = [
            ...currentResults.unique.map(r => ({ ...r, status: 'New' })),
            ...currentResults.duplicates.map(r => ({ ...r, status: 'Duplicate' }))
        ];
    } else if (filter === 'new') {
        items = currentResults.unique.map(r => ({ ...r, status: 'New' }));
    } else if (filter === 'duplicates') {
        items = currentResults.duplicates.map(r => ({ ...r, status: 'Duplicate' }));
    }

    if (items.length === 0) {
        resultsPreviewBody.innerHTML = '<tr><td colspan="2" style="padding: 20px; text-align: center; color: var(--text-muted);">No results found</td></tr>';
        return;
    }

    items.forEach(item => {
        const row = document.createElement('tr');
        row.style.borderBottom = '1px solid var(--border)';
        const statusColor = item.status === 'New' ? 'var(--accent-green)' : 'var(--accent-red)';
        const badgeBg = item.status === 'New' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)';
        row.innerHTML = `
            <td style="padding: 10px; font-weight: 500;">${item.name}</td>
            <td style="padding: 10px; text-align: center;">
                <span style="background: ${badgeBg}; color: ${statusColor}; padding: 2px 8px; border-radius: 4px; font-size: 0.65rem; font-weight: 700; text-transform: uppercase;">${item.status}</span>
            </td>
        `;
        resultsPreviewBody.appendChild(row);
    });
}

filterRadios.forEach(radio => {
    radio.addEventListener('change', (e) => {
        renderPreview(e.target.value);
    });
});

// === HISTORY PAGE ===
async function loadHistory() {
    const container = document.getElementById('history-list');
    container.innerHTML = '<div class="loading-msg">Loading history...</div>';
    try {
        const res = await fetch('/api/history');
        const history = await res.json();
        if (!history.length) {
            container.innerHTML = '<div class="empty-state"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="48" height="48"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg><p>No extraction history yet</p><span>Run your first extraction to see results here</span></div>';
            return;
        }
        container.innerHTML = history.map(h => `
            <div class="history-item">
                <div class="history-info">
                    <div class="history-title">${h.niche} — ${h.location}</div>
                    <div class="history-meta">${h.leads} leads · ${h.emails} emails · ${new Date(h.created_at).toLocaleString()}</div>
                </div>
                <div class="history-actions">
                    <a href="/api/download/${h.file}" class="btn-sm btn-dl" title="Download">↓ CSV</a>
                    <button class="btn-sm btn-del" onclick="deleteHistory('${h.id}')" title="Delete">✕</button>
                </div>
            </div>
        `).join('');
    } catch (e) {
        container.innerHTML = '<div class="empty-state"><p>Failed to load history</p></div>';
    }
}

window.deleteHistory = async function (id) {
    if (!confirm('Delete this extraction record?')) return;
    await fetch(`/api/history/${id}`, { method: 'DELETE' });
    loadHistory();
};

// === DATASETS PAGE ===
async function loadDatasets() {
    const container = document.getElementById('datasets-list');
    container.innerHTML = '<div class="loading-msg">Loading datasets...</div>';
    try {
        const res = await fetch('/api/datasets');
        const datasets = await res.json();
        if (!datasets.length) {
            container.innerHTML = '<div class="empty-state"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="48" height="48"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg><p>No datasets yet</p><span>Completed extractions will appear here</span></div>';
            return;
        }
        container.innerHTML = datasets.map(d => {
            const sizeKb = (d.size_bytes / 1024).toFixed(1);
            return `
            <div class="dataset-item">
                <div class="dataset-icon">📄</div>
                <div class="dataset-info">
                    <div class="dataset-name">${d.filename}</div>
                    <div class="dataset-meta">${d.rows} rows · ${sizeKb} KB · ${new Date(d.modified).toLocaleDateString()}</div>
                </div>
                <div class="dataset-actions">
                    <a href="/api/download/${d.filename}" class="btn-sm btn-dl">↓ Download</a>
                    <button class="btn-sm btn-del" onclick="deleteDataset('${d.filename}')">✕</button>
                </div>
            </div>`;
        }).join('');
    } catch (e) {
        container.innerHTML = '<div class="empty-state"><p>Failed to load datasets</p></div>';
    }
}

window.deleteDataset = async function (filename) {
    if (!confirm('Delete this dataset?')) return;
    await fetch(`/api/datasets/${filename}`, { method: 'DELETE' });
    loadDatasets();
};

// === PROXIES PAGE ===
async function loadProxies() {
    const container = document.getElementById('proxy-list-items');
    try {
        const res = await fetch('/api/proxies');
        const data = await res.json();
        renderProxyList(data.proxies || []);
    } catch (e) {
        container.innerHTML = '<div class="empty-state"><p>Failed to load proxies</p></div>';
    }
}

function renderProxyList(proxies) {
    const container = document.getElementById('proxy-list-items');
    if (!proxies.length) {
        container.innerHTML = '<div class="empty-state"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="48" height="48"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/><line x1="12" y1="2" x2="12" y2="22"/></svg><p>No proxies configured</p><span>Add proxies below for stealth scraping</span></div>';
        return;
    }
    container.innerHTML = proxies.map((p, i) => `
        <div class="proxy-item">
            <span class="proxy-dot ${p.active !== false ? 'active' : ''}"></span>
            <span class="proxy-url">${p.url}</span>
            <button class="btn-sm btn-del" onclick="removeProxy(${i})">✕</button>
        </div>
    `).join('');
}

window.addProxy = async function () {
    const input = document.getElementById('new-proxy-input');
    const url = input.value.trim();
    if (!url) return;
    const res = await fetch('/api/proxies');
    const data = await res.json();
    const proxies = data.proxies || [];
    proxies.push({ url, active: true });
    await fetch('/api/proxies', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ proxies }) });
    input.value = '';
    loadProxies();
};

window.removeProxy = async function (index) {
    const res = await fetch('/api/proxies');
    const data = await res.json();
    const proxies = data.proxies || [];
    proxies.splice(index, 1);
    await fetch('/api/proxies', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ proxies }) });
    loadProxies();
};

// === REFINE PAGE ===
const refineUploadZone = document.getElementById('refine-upload-zone');
const refineFileInput = document.getElementById('refine-file-input');
const refineStatus = document.getElementById('refine-status');
const refineDownloadBtn = document.getElementById('refine-download-btn');

if (refineUploadZone) {
    refineUploadZone.addEventListener('click', () => refineFileInput.click());

    refineUploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        refineUploadZone.classList.add('dragover');
    });

    refineUploadZone.addEventListener('dragleave', () => {
        refineUploadZone.classList.remove('dragover');
    });

    refineUploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        refineUploadZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            handleRefineFile(e.dataTransfer.files[0]);
        }
    });

    refineFileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleRefineFile(e.target.files[0]);
        }
    });
}

async function handleRefineFile(file) {
    if (!file.name.endsWith('.csv')) {
        alert('Please upload a CSV file.');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    refineStatus.style.display = 'none';
    const uploadText = refineUploadZone.querySelector('.upload-text');
    const originalText = uploadText.innerText;
    uploadText.innerText = 'Processing your leads...';
    refineUploadZone.style.pointerEvents = 'none';
    refineUploadZone.style.opacity = '0.6';

    try {
        const response = await fetch('/api/refine', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();

        if (data.status === 'success') {
            document.getElementById('refine-initial').innerText = data.initial_count;
            document.getElementById('refine-removed').innerText = data.duplicates_removed;
            document.getElementById('refine-clean').innerText = data.refined_count;
            refineDownloadBtn.href = `/api/download/${data.file}`;
            refineStatus.style.display = 'block';
        } else {
            alert('Refinement failed: ' + data.message);
        }
    } catch (err) {
        alert('Error connecting to server.');
    } finally {
        uploadText.innerText = originalText;
        refineUploadZone.style.pointerEvents = 'auto';
        refineUploadZone.style.opacity = '1';
    }
}

// === EMAIL ENRICHER PAGE ===
const enricherUploadZone = document.getElementById('enricher-upload-zone');
const enricherFileInput = document.getElementById('enricher-file-input');
const enricherProgress = document.getElementById('enricher-progress');
const enricherResults = document.getElementById('enricher-results');
const enricherConcurrency = document.getElementById('enricher-concurrency');
const enricherConcurrencyValue = document.getElementById('enricher-concurrency-value');

let pendingEnricherFile = null;

if (enricherConcurrency) {
    enricherConcurrency.addEventListener('input', () => {
        const val = ((enricherConcurrency.value - enricherConcurrency.min) / (enricherConcurrency.max - enricherConcurrency.min)) * 100;
        enricherConcurrency.style.setProperty('--val', val + '%');
        enricherConcurrencyValue.textContent = enricherConcurrency.value + ' Threads';
    });
    // Init slider visual
    const initVal = ((enricherConcurrency.value - enricherConcurrency.min) / (enricherConcurrency.max - enricherConcurrency.min)) * 100;
    enricherConcurrency.style.setProperty('--val', initVal + '%');
}

if (enricherUploadZone) {
    enricherUploadZone.addEventListener('click', () => enricherFileInput.click());

    enricherUploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        enricherUploadZone.classList.add('dragover');
    });

    enricherUploadZone.addEventListener('dragleave', () => {
        enricherUploadZone.classList.remove('dragover');
    });

    enricherUploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        enricherUploadZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            onEnricherFileSelected(e.dataTransfer.files[0]);
        }
    });

    enricherFileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            onEnricherFileSelected(e.target.files[0]);
        }
    });
}

function onEnricherFileSelected(file) {
    if (!file.name.endsWith('.csv')) {
        alert('Please select a CSV file.');
        return;
    }
    pendingEnricherFile = file;
    document.getElementById('enricher-file-name').innerText = file.name;
    document.getElementById('enricher-file-display').style.display = 'block';
    
    const startBtn = document.getElementById('enricher-start-btn');
    if (startBtn) {
        startBtn.disabled = false;
        startBtn.style.opacity = '1';
    }
    
    if (enricherResults) enricherResults.style.display = 'none';
}

const enricherFileRemoveBtn = document.getElementById('enricher-file-remove');
if (enricherFileRemoveBtn) {
    enricherFileRemoveBtn.addEventListener('click', () => {
        pendingEnricherFile = null;
        document.getElementById('enricher-file-display').style.display = 'none';
        const startBtn = document.getElementById('enricher-start-btn');
        if (startBtn) {
            startBtn.disabled = true;
            startBtn.style.opacity = '0.6';
        }
        if (enricherFileInput) enricherFileInput.value = '';
    });
}

const enricherStartBtn = document.getElementById('enricher-start-btn');
if (enricherStartBtn) {
    enricherStartBtn.addEventListener('click', () => {
        if (pendingEnricherFile) {
            document.getElementById('enricher-file-display').style.display = 'none';
            handleEnricherFile(pendingEnricherFile);
        } else {
            alert('Please select a CSV file first.');
        }
    });
}

async function handleEnricherFile(file) {
    if (!file.name.endsWith('.csv')) {
        alert('Please upload a CSV file.');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('concurrency', enricherConcurrency ? enricherConcurrency.value : '5');

    // Add email limit toggle value
    const extractAll = document.getElementById('enricher-extract-all').checked;
    formData.append('email_limit', extractAll ? 0 : 1);

    // Add dedicated proxies from enricher page if present
    const enricherProxies = document.getElementById('enricher-proxies');
    const proxyTypeEnrich = document.getElementById('proxy-type-enrich').value;
    if (enricherProxies && enricherProxies.value.trim()) {
        // Apply protocol prefix to each proxy line
        const formattedProxies = enricherProxies.value.trim().split('\n').map(p => {
            p = p.trim();
            if (p && !p.includes('://')) {
                return proxyTypeEnrich + p;
            }
            return p;
        }).join('\n');
        formData.append('proxies', formattedProxies);
    }

    // Add strict mode
    const strictModeEnrich = document.getElementById('strict-mode-enrich').checked;
    formData.append('strict_mode', strictModeEnrich);

    // Hide results, show progress
    if (enricherResults) enricherResults.style.display = 'none';
    if (enricherProgress) enricherProgress.style.display = 'block';
    enricherUploadZone.style.opacity = '0.5';
    enricherUploadZone.style.pointerEvents = 'none';

    const statusText = document.getElementById('enricher-status-text');
    const statusSub = document.getElementById('enricher-status-sub');
    const progressBarEl = document.getElementById('enricher-progress-bar');
    const spinnerEl = document.getElementById('enricher-spinner');

    if (statusText) statusText.innerText = 'Uploading CSV...';
    if (statusSub) statusSub.innerText = 'Preparing email enrichment';
    if (progressBarEl) { progressBarEl.classList.add('indeterminate'); progressBarEl.style.width = '40%'; }

    try {
        const response = await fetch('/api/enrich-csv', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();

        if (data.error) {
            alert('Error: ' + data.error);
            resetEnricherUI();
            return;
        }

        pollEnrichStatus(data.job_id);
    } catch (err) {
        alert('Error connecting to server: ' + err.message);
        resetEnricherUI();
    }
}

function pollEnrichStatus(jobId) {
    const statusText = document.getElementById('enricher-status-text');
    const statusSub = document.getElementById('enricher-status-sub');
    const progressBarEl = document.getElementById('enricher-progress-bar');
    const spinnerEl = document.getElementById('enricher-spinner');

    const intv = setInterval(async () => {
        try {
            const res = await fetch(`/api/jobs/${jobId}`);
            const data = await res.json();

            if (statusText) statusText.innerText = data.status;

            const enrichMatch = data.status.match(/\((\d+)\/(\d+)\)/);
            if (enrichMatch) {
                const current = parseInt(enrichMatch[1]);
                const total = parseInt(enrichMatch[2]);
                const pct = Math.round((current / total) * 100);
                if (progressBarEl) {
                    progressBarEl.classList.remove('indeterminate');
                    progressBarEl.style.width = pct + '%';
                }
                if (statusSub) statusSub.innerText = `Scraping emails for lead ${current} of ${total}`;
            }

            if (data.status === 'Complete') {
                clearInterval(intv);
                if (spinnerEl) spinnerEl.style.display = 'none';
                if (progressBarEl) {
                    progressBarEl.classList.remove('indeterminate');
                    progressBarEl.style.width = '100%';
                }
                if (statusSub) statusSub.innerText = `Done! ${data.email_count || 0} of ${data.result_count || '?'} leads got emails.`;

                // Show results card
                const totalCount = data.result_count || 0;
                const emailCount = data.email_count || 0;
                const noEmail = totalCount - emailCount;
                const duplicates = data.duplicates_skipped || 0;

                document.getElementById('enricher-total').innerText = totalCount;
                document.getElementById('enricher-with-email').innerText = emailCount;
                document.getElementById('enricher-no-email').innerText = noEmail >= 0 ? noEmail : 0;
                const enricherDuplicates = document.getElementById('enricher-duplicates');
                if (enricherDuplicates) enricherDuplicates.innerText = duplicates;

                if (data.file) {
                    document.getElementById('enricher-download-btn').href = `/api/download/${data.file}`;
                }

                if (enricherResults) enricherResults.style.display = 'block';
                showNotification();
                resetEnricherUI();
            } else if (data.status.startsWith('Error')) {
                clearInterval(intv);
                if (spinnerEl) spinnerEl.style.display = 'none';
                if (progressBarEl) {
                    progressBarEl.classList.remove('indeterminate');
                    progressBarEl.style.width = '0%';
                }
                if (statusSub) statusSub.innerText = data.status;
                resetEnricherUI();
            }
        } catch (err) { /* retry silently */ }
    }, 1500);
}

function resetEnricherUI() {
    if (enricherUploadZone) {
        enricherUploadZone.style.opacity = '1';
        enricherUploadZone.style.pointerEvents = 'auto';
    }
    if (enricherFileInput) enricherFileInput.value = '';
    
    pendingEnricherFile = null;
    const fileDisplay = document.getElementById('enricher-file-display');
    if (fileDisplay) fileDisplay.style.display = 'none';
    
    const startBtn = document.getElementById('enricher-start-btn');
    if (startBtn) {
        startBtn.disabled = true;
        startBtn.style.opacity = '0.6';
    }
}

// Proxy verification for Enricher page
const enricherVerifyProxies = document.getElementById('enricher-verify-proxies');
const enricherProxyStatus = document.getElementById('enricher-proxy-status');

if (enricherVerifyProxies) {
    enricherVerifyProxies.addEventListener('click', async () => {
        const enricherProxies = document.getElementById('enricher-proxies');
        if (!enricherProxies || !enricherProxies.value.trim()) {
            alert('Please enter at least one proxy to verify.');
            return;
        }

        enricherVerifyProxies.disabled = true;
        enricherVerifyProxies.style.opacity = '0.7';
        if (enricherProxyStatus) {
            enricherProxyStatus.innerText = 'Verifying...';
            enricherProxyStatus.style.color = 'var(--text-muted)';
        }

        try {
            const response = await fetch('/api/test-proxy', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ proxy: enricherProxies.value.trim() })
            });
            const data = await response.json();

            if (enricherProxyStatus) {
                if (data.status === 'success') {
                    enricherProxyStatus.innerText = `✓ Working (IP: ${data.ip})`;
                    enricherProxyStatus.style.color = 'var(--accent-green)';
                } else {
                    enricherProxyStatus.innerText = `✗ Failed: ${data.message}`;
                    enricherProxyStatus.style.color = 'var(--accent-red)';
                }
            }
        } catch (err) {
            if (enricherProxyStatus) {
                enricherProxyStatus.innerText = '✗ Error connecting to server';
                enricherProxyStatus.style.color = 'var(--accent-red)';
            }
        } finally {
            enricherVerifyProxies.disabled = false;
            enricherVerifyProxies.style.opacity = '1';
        }
    });
}

