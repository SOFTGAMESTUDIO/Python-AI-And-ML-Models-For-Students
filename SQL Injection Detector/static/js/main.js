// DOM Elements
const targetUrlInput = document.getElementById('targetUrl');
const deepScanCheckbox = document.getElementById('deepScan');
const startScanBtn = document.getElementById('startScan');
const scanProgress = document.getElementById('scanProgress');
const resultsSection = document.getElementById('results');
const reportsSection = document.getElementById('reportsSection');
const scannerSection = document.getElementById('scannerSection');
const docsSection = document.getElementById('docsSection');
const reportsLink = document.getElementById('reportsLink');
const docsLink = document.getElementById('docsLink');
const toast = document.getElementById('toast');

// Navigation
document.querySelectorAll('.nav-links a').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        const text = link.textContent.toLowerCase();
        
        // Hide all sections
        scannerSection.style.display = 'none';
        reportsSection.style.display = 'none';
        docsSection.style.display = 'none';
        
        // Show selected section
        if (text === 'scanner') {
            scannerSection.style.display = 'block';
        } else if (text === 'reports') {
            reportsSection.style.display = 'block';
            loadReports();
        } else if (text === 'documentation') {
            docsSection.style.display = 'block';
        }
        
        // Update active state
        document.querySelectorAll('.nav-links a').forEach(a => a.classList.remove('active'));
        link.classList.add('active');
    });
});

// Start Scan
startScanBtn.addEventListener('click', async () => {
    const url = targetUrlInput.value.trim();
    if (!url) {
        showToast('Please enter a URL to scan', 'error');
        return;
    }
    
    // Validate URL format
    let targetUrl = url;
    if (!targetUrl.startsWith('http://') && !targetUrl.startsWith('https://')) {
        targetUrl = 'https://' + targetUrl;
    }
    
    const deepScan = deepScanCheckbox.checked;
    
    // Show progress
    scanProgress.style.display = 'block';
    startScanBtn.disabled = true;
    resultsSection.style.display = 'none';
    
    try {
        const response = await fetch('/api/scan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                url: targetUrl,
                deep_scan: deepScan
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayResults(data);
            showToast(`Scan completed! Found ${data.total_vulnerabilities} vulnerabilities`, 'success');
        } else {
            showToast(data.error || 'Scan failed', 'error');
        }
    } catch (error) {
        showToast('Error connecting to server', 'error');
        console.error('Scan error:', error);
    } finally {
        scanProgress.style.display = 'none';
        startScanBtn.disabled = false;
    }
});

// Display Results
function displayResults(data) {
    resultsSection.style.display = 'block';
    
    // Update statistics
    const totalVulns = data.vulnerabilities.length;
    const criticalVulns = data.vulnerabilities.filter(v => v.severity === 'CRITICAL' || v.severity === 'HIGH').length;
    const highVulns = data.vulnerabilities.filter(v => v.severity === 'HIGH').length;
    
    document.getElementById('totalVulns').textContent = totalVulns;
    document.getElementById('criticalVulns').textContent = criticalVulns;
    document.getElementById('highVulns').textContent = highVulns;
    
    // Display vulnerabilities
    const vulnList = document.getElementById('vulnerabilitiesList');
    
    if (totalVulns === 0) {
        vulnList.innerHTML = `
            <div class="vuln-card">
                <div style="text-align: center; padding: 2rem;">
                    <h3>✅ No SQL Injection Vulnerabilities Found</h3>
                    <p>The website appears to be secure against basic SQL injection attacks.</p>
                </div>
            </div>
        `;
        return;
    }
    
    vulnList.innerHTML = data.vulnerabilities.map(vuln => `
        <div class="vuln-card ${vuln.severity.toLowerCase()}">
            <div class="vuln-header">
                <span class="vuln-parameter">Parameter: ${escapeHtml(vuln.parameter)}</span>
                <span class="vuln-badge ${vuln.severity.toLowerCase()}">${vuln.severity}</span>
            </div>
            <div class="vuln-header">
                <span style="font-size: 0.9rem; color: #666;">Type: ${escapeHtml(vuln.type)}</span>
                <span style="font-size: 0.9rem; color: #666;">Location: ${escapeHtml(vuln.location)}</span>
            </div>
            <div class="vuln-payload">
                <strong>Payload:</strong> ${escapeHtml(vuln.payload)}
            </div>
            <div class="vuln-evidence">
                <strong>Evidence:</strong> ${escapeHtml(vuln.evidence)}
            </div>
        </div>
    `).join('');
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Load Reports
async function loadReports() {
    const reportsList = document.getElementById('reportsList');
    reportsList.innerHTML = '<div class="loading">Loading reports...</div>';
    
    try {
        const response = await fetch('/api/reports');
        const data = await response.json();
        
        if (data.reports && data.reports.length > 0) {
            reportsList.innerHTML = data.reports.map(report => `
                <div class="report-card">
                    <div class="report-info">
                        <h4>${escapeHtml(report.target)}</h4>
                        <p>Scan ID: ${escapeHtml(report.scan_id)} | Date: ${new Date(report.timestamp).toLocaleString()}</p>
                        <p>Found: ${report.vulnerabilities} vulnerabilities</p>
                    </div>
                    <div class="report-actions">
                        <button class="btn-secondary" onclick="viewReport('${report.filename}')">View</button>
                        <button class="btn-secondary" onclick="downloadReport('${report.filename}')">Download</button>
                    </div>
                </div>
            `).join('');
        } else {
            reportsList.innerHTML = '<div class="loading">No reports found. Start a scan to generate reports.</div>';
        }
    } catch (error) {
        reportsList.innerHTML = '<div class="loading">Error loading reports</div>';
        console.error('Error loading reports:', error);
    }
}

// View Report
window.viewReport = async (filename) => {
    try {
        const response = await fetch(`/api/reports/${filename}`);
        const data = await response.json();
        
        // Display report in a modal
        const reportContent = JSON.stringify(data, null, 2);
        const modal = document.createElement('div');
        modal.style.position = 'fixed';
        modal.style.top = '0';
        modal.style.left = '0';
        modal.style.width = '100%';
        modal.style.height = '100%';
        modal.style.backgroundColor = 'rgba(0,0,0,0.8)';
        modal.style.zIndex = '1000';
        modal.style.display = 'flex';
        modal.style.alignItems = 'center';
        modal.style.justifyContent = 'center';
        
        modal.innerHTML = `
            <div style="background: white; border-radius: 10px; max-width: 80%; max-height: 80%; overflow: auto; padding: 2rem;">
                <h2>Scan Report</h2>
                <pre style="background: #f5f5f5; padding: 1rem; border-radius: 5px; overflow-x: auto;">${escapeHtml(reportContent)}</pre>
                <button onclick="this.closest('div').remove()" style="margin-top: 1rem; padding: 0.5rem 1rem;">Close</button>
            </div>
        `;
        
        document.body.appendChild(modal);
    } catch (error) {
        showToast('Error loading report', 'error');
    }
};

// Download Report
window.downloadReport = async (filename) => {
    window.open(`/api/export/${filename}`, '_blank');
    showToast('Downloading report...', 'success');
};

// Utility Functions
function showToast(message, type = 'info') {
    toast.textContent = message;
    toast.style.display = 'block';
    toast.style.background = type === 'error' ? '#dc3545' : '#28a745';
    
    setTimeout(() => {
        toast.style.display = 'none';
    }, 3000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize
console.log('SQL Injection Detector loaded');