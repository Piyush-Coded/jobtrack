/**
 * JobTrack - Jobs JavaScript
 * Handles job search, listing, and details
 */

const API_BASE = (() => {
    const hostname = window.location.hostname;
    // Production Render URL
    if (hostname === 'jobtrack-frontend' || hostname.includes('onrender.com')) {
        return 'https://jobtrack-api-gwbb.onrender.com/api';
    }
    // Development
    return 'http://127.0.0.1:8000/api';
})();

let currentPage = 1;
let totalPages = 1;
let allJobs = [];

function renderJobs(jobs) {
    const grid = document.getElementById('jobs-grid');
    if (!grid) return;
    
    if (jobs.length === 0) {
        grid.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 3rem; color: var(--text-secondary);">
                <p>No jobs found. Try adjusting your search criteria.</p>
            </div>
        `;
        return;
    }
    
    allJobs = jobs;
    grid.innerHTML = jobs.map(job => `
        <article class="job-card" data-job-id="${job.id}">
            <div class="job-card-header">
                <span class="job-tag">${job.employment_type || 'Full-time'}</span>
            </div>
            <div class="job-card-content">
                <h3>${job.title}</h3>
                <div class="meta">
                    <span>${job.company_name || 'Company'}</span>
                    <span>${job.location || 'Location'}</span>
                </div>
                <p>${job.description ? job.description.substring(0, 120) + '...' : 'No description available'}</p>
                <div class="job-meta">
                    <span><i class="fas fa-briefcase"></i> ${job.experience_min || 0}+ years</span>
                    <span><i class="fas fa-building"></i> ${job.work_mode || 'Hybrid'}</span>
                </div>
            </div>
            <div class="job-card-footer">
                <span class="salary">₹${job.salary_min || 0} - ₹${job.salary_max || 0}/yr</span>
                <div class="apply-actions">
                    <button class="btn-apply" onclick="applyToJob(${job.id}, this)">Apply</button>
                    <button class="btn-save" onclick="saveJob(${job.id}, this)">Save</button>
                </div>
            </div>
        </article>
    `).join('');
    
    // Add click handlers for job cards
    setupJobCardClicks();
    
    renderPagination();
}

function setupJobCardClicks() {
    const jobCards = document.querySelectorAll('.job-card');
    
    jobCards.forEach(card => {
        card.addEventListener('click', function(e) {
            // Don't trigger if clicking on buttons
            if (e.target.tagName === 'BUTTON' || e.target.parentTag === 'BUTTON') {
                return;
            }
            
            const jobId = parseInt(this.dataset.jobId);
            openJobDetails(jobId);
        });
    });
}

function openJobDetails(jobId) {
    const job = allJobs.find(j => j.id === jobId);
    if (!job) return;
    
    // Build details HTML
    const skillsHtml = job.skills ? job.skills.split(',').map(s => `<span class="job-detail-skill">${s.trim()}</span>`).join('') : '';
    
    const detailsHTML = `
        <div class="job-detail-hero">
            <div class="container">
                <h1>${job.title}</h1>
                <div class="job-detail-meta">
                    <span><strong>Company:</strong> ${job.company_name}</span>
                    <span><strong>Location:</strong> ${job.location}</span>
                    <span><strong>Salary:</strong> ₹${job.salary_min || 0} - ₹${job.salary_max || 0}/yr</span>
                    <span><strong>Experience:</strong> ${job.experience_min || 0}-${job.experience_max || 5}+ years</span>
                    <span><strong>Employment:</strong> ${job.employment_type || 'Full-time'}</span>
                    <span><strong>Work Mode:</strong> ${job.work_mode || 'Hybrid'}</span>
                </div>
            </div>
        </div>
        
        <div class="container">
            <div class="row">
                <div class="col-lg-8">
                    <div class="job-detail-section">
                        <h2>About the Role</h2>
                        <p>${job.description || 'Description not available'}</p>
                    </div>
                    
                    <div class="job-detail-section">
                        <h2>Requirements</h2>
                        <p>${job.requirements || 'Not specified'}</p>
                    </div>
                    
                    <div class="job-detail-section">
                        <h2>Skills</h2>
                        <div class="job-detail-skills">
                            ${skillsHtml}
                        </div>
                    </div>
                    
                    <div class="job-detail-section">
                        <h2>Education</h2>
                        <p>${job.education || 'Not specified'}</p>
                    </div>
                    
                    <div class="job-detail-section">
                        <h2>Benefits</h2>
                        <p>${job.benefits || 'Not specified'}</p>
                    </div>
                </div>
                
                <div class="col-lg-4">
                    <div class="job-detail-section">
                        <h2>Company</h2>
                        <p>${job.company_description || 'Information not available'}</p>
                        
                        <strong>Industry:</strong> ${job.industry || 'Not specified'}<br>
                        <strong>Company Size:</strong> ${job.company_size || 'Not specified'}<br>
                        <strong>Website:</strong> <a href="${job.website || '#'}" target="_blank">${website || 'Not available'}</a>
                    </div>
                    
                    <div class="job-detail-section">
                        <h2>Similar Jobs</h2>
                        <p>Loading similar jobs...</p>
                    </div>
                    
                    <div class="job-detail-section">
                        <button class="btn-primary" onclick="applyToJob(${job.id}, event.target)">Apply Now</button>
                    </div>
                    
                    <div class="job-detail-section">
                        <button class="btn-save" onclick="saveJob(${job.id}, event.target)">Save Job</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Show in a modal or redirect to details page
    const modal = document.querySelector('.modal') || createModal();
    modal.innerHTML = detailsHTML + `
        <button class="close-btn" onclick="closeJobDetails()">&times;</button>
    `;
    modal.classList.add('active');
}

function closeJobDetails() {
    const modal = document.querySelector('.modal');
    if (modal) modal.classList.remove('active');
}

function createModal() {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <button class="close-btn" onclick="closeJobDetails()">&times;</button>
            <div id="job-details-content"></div>
        </div>
    `;
    document.body.appendChild(modal);
    return modal;
}

async function loadJobs(params = {}) {
    try {
        const query = new URLSearchParams(params).toString();
        const response = await fetch(`${API_BASE}/api/jobs?${query}`);
        const data = await response.json();
        
        if (response.ok) {
            renderJobs(data.jobs || data);
            currentPage = data.page || 1;
            totalPages = data.total_pages || 1;
            renderPagination();
            
            // Update job count information
            updateJobCount(data.total || jobs.length);
        } else {
            console.error('Failed to load jobs');
            showError('Failed to load jobs. Please try again.');
        }
    } catch (error) {
        console.error('Error loading jobs:', error);
        showError('Network error. Please try again.');
    }
}

function updateJobCount(total) {
    // Could update a header count
    const countElement = document.querySelector('.job-count');
    if (countElement) {
        countElement.textContent = `${total} jobs found`;
    }
}

function renderPagination() {
    const pagination = document.getElementById('pagination');
    if (!pagination) return;
    
    let pages = [];
    
    // Always show first page
    pages.push({ number: 1, disabled: currentPage === 1 });
    
    // Show ellipsis if needed
    if (currentPage > 3) {
        pages.push({ number: '...', disabled: true });
    }
    
    // Show page numbers around current page
    const start = Math.max(2, currentPage - 1);
    const end = Math.min(totalPages - 1, currentPage + 1);
    
    for (let i = start; i <= end; i++) {
        pages.push({ number: i, disabled: currentPage === i });
    }
    
    if (currentPage < totalPages - 1) {
        pages.push({ number: '...', disabled: true });
    }
    
    // Always show last page
    if (totalPages > 1) {
        pages.push({ number: totalPages, disabled: currentPage === totalPages });
    }
    
    pagination.innerHTML = pages.map(page => `
        <button class="page-btn ${page.disabled ? 'disabled' : ''}" 
                onclick="loadJobs({page: ${page.number}})"
                ${page.disabled ? 'disabled' : ''}>
            ${page.number}
        </button>
    `).join('');
}

function filterJobs() {
    const searchInput = document.getElementById('job-search')?.value || '';
    const locationSelect = document.getElementById('job-location')?.value || '';
    const employmentType = document.querySelector('input[name="employment"]:checked')?.value || '';
    
    const params = {
        search: searchInput,
        location: locationSelect,
    };
    
    if (employmentType) {
        params.employment_type = employmentType;
    }
    
    loadJobs(params);
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Setup search form
    const searchBtn = document.getElementById('search-btn');
    if (searchBtn) {
        searchBtn.addEventListener('click', filterJobs);
    }
    
    // Allow Enter key to search
    const searchInput = document.getElementById('job-search');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                filterJobs();
            }
        });
    }
    
    // Load initial jobs
    loadJobs();
});