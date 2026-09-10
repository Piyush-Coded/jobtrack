/**
 * JobTrack - Authentication JavaScript
 * Handles login, registration, and auth state
 */

// API base URL - will be overridden based on environment
// Development: http://127.0.0.1:8000
// Production: https://jobtrack-api-gwbb.onrender.com
const API_BASE = (() => {
    const hostname = window.location.hostname;
    // Production Render URL
    if (hostname === 'jobtrack-frontend' || hostname.includes('onrender.com')) {
        return 'https://jobtrack-api-gwbb.onrender.com/api';
    }
    // Development
    return 'http://127.0.0.1:8000/api';
})();

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    errorDiv.style.cssText = 'background: #fee2e2; color: #dc2626; padding: 0.8rem; border-radius: 6px; margin-bottom: 1rem; text-align: center; font-size: 0.85rem; border: 1px solid #fecaca;';
    
    // Remove existing error messages
    const existing = document.querySelector('.error-message');
    if (existing) existing.remove();
    
    // Insert at the beginning of modal content
    const modalContent = document.querySelector('.modal-content');
    if (modalContent) {
        modalContent.insertBefore(errorDiv, modalContent.firstChild);
    }
    
    // Auto-remove after 5 seconds
    setTimeout(() => errorDiv.remove(), 5000);
}

function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'success-message';
    successDiv.textContent = message;
    successDiv.style.cssText = 'background: #d1fae5; color: #059669; padding: 0.8rem; border-radius: 6x; margin-bottom: 1rem; text-align: center; font-size: 0.85rem; border: 1px solid #a3e635;';
    
    // Remove existing success messages
    const existing = document.querySelector('.success-message');
    if (existing) existing.remove();
    
    const modalContent = document.querySelector('.modal-content');
    if (modalContent) {
        modalContent.insertBefore(successDiv, modalContent.firstChild);
    }
    
    setTimeout(() => successDiv.remove(), 5000);
}

function setAuthButtons(isLoggedIn, role) {
    const authLink = document.getElementById('auth-link');
    const registerLink = document.getElementById('register-link');
    const searchBox = document.querySelector('.search-box');
    const jobsGrid = document.getElementById('jobs-grid');
    
    if (isLoggedIn) {
        // Hide auth links when logged in
        if (authLink) authLink.style.display = 'none';
        if (registerLink) registerLink.style.display = 'none';
        
        // Show search when logged in
        if (searchBox) searchBox.style.display = 'block';
        
        // Role-specific UI updates
        if (role === 'recruiter') {
            // Recruiter-specific buttons/actions
            if (jobsGrid) {
                // Add recruiter CTA area
            }
        } else if (role === 'job_seeker') {
            // Job seeker-specific buttons/actions
        }
    } else {
        if (authLink) authLink.style.display = 'block';
        if (registerLink) registerLink.style.display = 'block';
        if (searchBox) searchBox.style.display = 'block';
    }
}

function setLoading(button, isLoading) {
    if (isLoading) {
        button.disabled = true;
        button.style.opacity = '0.7';
        button.innerHTML = 'Loading...';
    } else {
        button.disabled = false;
        button.style.opacity = '1';
        button.innerHTML = isLoading === 'submit' ? 'Submit' : isLoading === 'save' ? 'Saved' : 'Apply';
    }
}

async function login(event) {
    event.preventDefault();
    
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    const button = event.target.querySelector('button');
    
    if (!email || !password) {
        showError('Please enter both email and password');
        return;
    }
    
    setLoading(button, true);
    
    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Store token and user role
            localStorage.setItem('jobtrack_token', data.access_token);
            localStorage.setItem('jobtrack_user_role', data.user.role);
            localStorage.setItem('jobtrack_user_name', data.user.full_name);
            
            showSuccess('Login successful!');
            
            // Update UI
            setAuthButtons(true, data.user.role);
            
            // Close modal
            const modal = document.querySelector('.modal');
            if (modal) modal.classList.remove('active');
            
            // Refresh jobs
            loadJobs();
            
            // Update dashboard if on dashboard page
            if (typeof updateDashboard === 'function') {
                updateDashboard();
            }
        } else {
            showError(data.detail || 'Login failed');
        }
    } catch (error) {
        showError('Network error. Please try again.');
    } finally {
        setLoading(button, false);
    }
}

async function register(event) {
    event.preventDefault();
    
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    const fullName = document.getElementById('register-fullname').value;
    const role = document.querySelector('input[name="role"]:checked').value;
    const button = event.target.querySelector('button');
    
    if (!email || !password || !fullName) {
        showError('Please fill in all fields');
        return;
    }
    
    setLoading(button, true);
    
    try {
        const response = await fetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password, full_name: fullName, role })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showSuccess('Registration successful! Please login.');
            
            // Switch to login tab after a moment
            setTimeout(() => {
                showLoginForm();
            }, 1500);
        } else {
            showError(data.detail || 'Registration failed');
        }
    } catch (error) {
        showError('Network error. Please try again.');
    } finally {
        setLoading(button, false);
    }
}

function showLoginForm() {
    const modal = document.querySelector('.modal');
    if (modal) modal.classList.remove('active');
}

async function applyToJob(jobId, button) {
    const token = localStorage.getItem('jobtrack_token');
    
    if (!token) {
        showError('Please login first');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/applications`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify({ job_id: jobId })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showSuccess('Application submitted successfully!');
            
            // Update UI - change button state
            if (button) {
                button.innerHTML = 'Applied';
                button.style.background = '#10b981';
                button.style.pointerEvents = 'none';
            }
            
            // Refresh jobs to show applied status
            loadJobs();
        } else {
            showError(data.detail || 'Application failed');
        }
    } catch (error) {
        showError('Network error. Please try again.');
    }
}

function saveJob(jobId, button) {
    const token = localStorage.getItem('jobtrack_token');
    
    if (!token) {
        showError('Please login first');
        return;
    }
    
    fetch(`${API_BASE}/api/saved-jobs/${jobId}/save`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccess('Job saved successfully!');
            // Update UI - change heart icon or button text
            if (button) {
                button.innerHTML = 'Saved';
                button.style.background = '#10b981';
                button.style.color = '#fff';
            }
        } else {
            showError(data.detail || 'Failed to save job');
        }
    })
    .catch(error => {
        showError('Network error. Please try again.');
    });
}

function unsaveJob(jobId, button) {
    const token = localStorage.getItem('jobtrack_token');
    
    if (!token) {
        showError('Please login first');
        return;
    }
    
    fetch(`${API_BASE}/api/saved-jobs/${jobId}/save`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccess('Job unsaved successfully!');
            // Update UI - change button back
            if (button) {
                button.innerHTML = 'Save';
                button.style.background = '';
                button.style.color = '';
            }
        } else {
            showError(data.detail || 'Failed to unsave job');
        }
    })
    .catch(error => {
        showError('Network error. Please try again.');
    });
}

function checkAuthState() {
    const token = localStorage.getItem('jobtrack_token');
    const role = localStorage.getItem('jobtrack_user_role');
    const userName = localStorage.getItem('jobtrack_user_name');
    
    if (token) {
        setAuthButtons(true, role);
        // Update welcome message if on dashboard
        if (userName && typeof updateWelcome === 'function') {
            updateWelcome(userName);
        }
    } else {
        setAuthButtons(false, null);
        if (userName && typeof clearWelcome === 'function') {
            clearWelcome();
        }
    }
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    checkAuthState();
});