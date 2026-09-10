// JobTrack Frontend — Vanilla JS
// ============================================================
// API base URL — change this for local vs production
// Local:  http://127.0.0.1:8000
// Render: https://jobtrack-api-gwbb.onrender.com
// ============================================================
const API_BASE = 'http://127.0.0.1:8000'; // <— adjust after deployment

// DOM elements
const tbody = document.getElementById('app-tbody');
const emptyState = document.getElementById('empty-state');
const appTable = document.getElementById('applications-table');
const searchInput = document.getElementById('search-input');
const statusFilter = document.getElementById('status-filter');
const totalAppsEl = document.getElementById('total-apps');
const byStatusEl = document.getElementById('by-status');
const byEmploymentEl = document.getElementById('by-employment');
const avgSalaryEl = document.getElementById('avg-salary');
const statsTotalEl = document.getElementById('stats-total');
const statsInterviewEl = document.getElementById('stats-interview');
const statsFulltimeEl = document.getElementById('stats-fulltime');
const statsParttimeEl = document.getElementById('stats-parttime');
const statsAvgSalaryEl = document.getElementById('stats-avg-salary');
const statsLoading = document.getElementById('stats-loading');
const statsContent = document.getElementById('stats-content');
const modal = document.getElementById('application-modal');
const modalTitle = document.getElementById('modal-title');
const applicationForm = document.getElementById('application-form');
const applicationIdInput = document.getElementById('application-id');
const appSearch = document.getElementById('search-input');
const appStatusFilter = document.getElementById('status-filter');

// State
let allApplications = [];
let editId = null;

// --- API helpers ---
async function api(method, endpoint, body = null) {
  const url = `${API_BASE}${endpoint}`;
  const options = {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  };
  const response = await fetch(url, options);
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || `HTTP ${response.status}`);
  }
  return response.json();
}

// --- Fetch Applications ---
async function loadApplications(filters = {}) {
  let url = `${API_BASE}/api/applications?`;
  const params = [];
  if (filters.search) params.push(`search=${encodeURIComponent(filters.search)}`);
  if (filters.status) params.push(`status=${filters.status}`);
  url += params.join('&') || '';
  try {
    const data = await api('GET', url);
    allApplications = data;
    renderApplications(data);
    toggleEmptyState(data.length === 0);
  } catch (err) {
    console.error(err);
    alert('Failed to load applications: ' + err.message);
  }
}

// --- Render Applications Table ---
function renderApplications(apps) {
  tbody.innerHTML = '';
  if (apps.length === 0) {
    emptyState.style.display = 'block';
    appTable.style.display = 'none';
    return;
  }
  emptyState.style.display = 'none';
  appTable.style.display = 'table';

  apps.forEach(app => {
    const tr = document.createElement('tr');

    const statusClass = {
      Applied: 'Applied',
      Interview: 'Interview',
      Offer: 'Offer',
      Rejected: 'Rejected',
    }[app.status] || '';

    tr.innerHTML = `
      <td>${escapeHtml(app.company_name)}</td>
      <td>${escapeHtml(app.job_title)}</td>
      <td>${escapeHtml(app.location)}</td>
      <td>${app.salary !== null && app.salary !== undefined ? `$${Number(app.salary).toLocaleString()}` : '—'}</td>
      <td>${formatDate(app.applied_date)}</td>
      <td><span class="status-badge status-${statusClass.toLowerCase()}">${escapeHtml(app.status)}</span></td>
      <td>
        <div class="action-btns">
          <button class="action-btn edit-btn" data-id="${app.id}">Edit</button>
          <button class="action-btn delete-btn" data-id="${app.id}">Delete</button>
        </div>
      </td>
    `;
    tbody.appendChild(tr);
  });

  // Attach event listeners after rendering
  document.querySelectorAll('.edit-btn').forEach(btn => {
    btn.addEventListener('click', () => openModal(parseInt(btn.dataset.id)));
  });
  document.querySelectorAll('.delete-btn').forEach(btn => {
    btn.addEventListener('click', () => confirmDelete(parseInt(btn.dataset.id)));
  });
}

// --- Helpers ---
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function formatDate(dateStr) {
  if (!dateStr) return '—';
  const d = new Date(dateStr);
  return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
}

// --- Statistics ---
async function loadStatistics() {
  try {
    const stats = await api('GET', `${API_BASE}/api/statistics`);
    updateStatsView(stats);
  } catch (err) {
    console.error(err);
    showError(statsLoading, 'Failed to load statistics');
  }
}

function updateStatsView(s) {
  totalAppsEl.textContent = s.total_applications || 0;
  byStatusEl.textContent = Object.values(s.by_status).reduce((a, b) => a + b, 0) || 0;
  byEmploymentEl.textContent = Object.values(s.by_employment_type).reduce((a, b) => a + b, 0) || 0;
  avgSalaryEl.textContent = s.average_salary !== null ? `$${s.average_salary}` : '—';

  statsTotalEl.textContent = s.total_applications || 0;
  statsInterviewEl.textContent = s.by_status.Interview || 0;
  statsFulltimeEl.textContent = s.by_employment_type.Full-time || 0;
  statsParttimeEl.textContent = s.by_employment_type.Part-time || 0;
  statsAvgSalaryEl.textContent = s.average_salary !== null ? `$${s.average_salary}` : '—';

  statsLoading.style.display = 'none';
  statsContent.style.display = 'block';
}

function showError(el, msg) {
  el.textContent = msg;
  el.style.display = 'block';
  statsLoading.style.display = 'none';
  statsContent.style.display = 'none';
}

// --- Modal ---
function openModal(id = null) {
  editId = id;
  if (editId) {
    const app = allApplications.find(a => a.id === editId);
    if (!app) { alert('Application not found'); return; }
    modalTitle.textContent = 'Edit Application';
    applicationForm.querySelector('[name="company_name"]').value = app.company_name || '';
    applicationForm.querySelector('[name="job_title"]').value = app.job_title || '';
    applicationForm.querySelector('[name="location"]').value = app.location || '';
    applicationForm.querySelector('[name="job_url"]').value = app.job_url || '';
    applicationForm.querySelector('[name="employment_type"]').value = app.employment_type || '';
    applicationForm.querySelector('[name="salary"]').value = app.salary || '';
    applicationForm.querySelector('[name="status"]').value = app.status || 'Applied';
    applicationForm.querySelector('[name="interview_date"]').value = app.interview_date ? new Date(app.interview_date).toISOString().split('T')[0] : '';
    applicationForm.querySelector('[name="notes"]').value = app.notes || '';
  } else {
    modalTitle.textContent = 'Add Application';
    applicationForm.reset();
    applicationIdInput.value = '';
    editId = null;
  }
  modal.style.display = 'flex';
}

function closeModal() {
  modal.style.display = 'none';
  applicationForm.reset();
}

// --- Delete confirmation ---
function confirmDelete(id) {
  if (confirm('Are you sure you want to delete this application?')) {
    deleteApplication(id);
  }
}

async function deleteApplication(id) {
  try {
    await api('DELETE', `/api/applications/${id}`);
    loadApplications({ search: appSearch.value.trim(), status: appStatusFilter.value });
    closeModal();
  } catch (err) {
    alert('Failed to delete: ' + err.message);
  }
}

// --- Form submit ---
applicationForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const formData = {};
  const form = e.target;
  const fields = ['company_name', 'job_title', 'location', 'job_url', 'employment_type', 'salary', 'status', 'interview_date', 'notes'];
  fields.forEach(field => {
    const val = form.elements[field].value;
    formData[field] = val !== '' ? val : null;
  });

  try {
    if (editId) {
      await api('PUT', `/api/applications/${editId}`, formData);
    } else {
      await api('POST', '/api/applications', formData);
    }
    loadApplications();
    closeModal();
  } catch (err) {
    alert('Failed: ' + err.message);
  }
});

// --- Init ---
document.addEventListener('DOMContentLoaded', () => {
  // Close modal on outside click
  modal.addEventListener('click', (e) => {
    if (e.target === modal) closeModal();
  });

  // Nav link active state
  document.querySelectorAll('.nav-links a').forEach(a => {
    a.addEventListener('click', () => {
      document.querySelectorAll('.nav-links a').forEach(x => x.classList.remove('active'));
      a.classList.add('active');
    });
  });

  // Load data
  loadApplications();
  loadStatistics();

  // Search/filter live updates
  appSearch.addEventListener('input', (e) => {
    loadApplications({ search: e.target.value.trim(), status: appStatusFilter.value });
  });
  appStatusFilter.addEventListener('change', (e) => {
    loadApplications({ search: appSearch.value.trim(), status: e.target.value });
  });
});