const BASE_URL = 'http://127.0.0.1:5000/api';

const api = {
    // Utility for headers
    getHeaders(isFormData = false) {
        const token = localStorage.getItem('access_token');
        const headers = {};
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        if (!isFormData) {
            headers['Content-Type'] = 'application/json';
        }
        return headers;
    },

    // Handle generic response
    async handleResponse(response) {
        const data = await response.json().catch(() => ({}));
        if (!response.ok) {
            if (response.status === 401) {
                // Token expired or invalid
                localStorage.removeItem('access_token');
                localStorage.removeItem('user');
                window.location.href = 'login.html';
            }
            throw new Error(data.error || 'Something went wrong');
        }
        return data;
    },

    // Auth
    async login(email, password) {
        const res = await fetch(`${BASE_URL}/auth/login`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify({ email, password })
        });
        return this.handleResponse(res);
    },

    async register(userData) {
        const res = await fetch(`${BASE_URL}/auth/register`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify(userData)
        });
        return this.handleResponse(res);
    },

    // Tickets
    async getTickets(filters = {}) {
        const queryParams = new URLSearchParams(filters).toString();
        const url = `${BASE_URL}/tickets${queryParams ? '?' + queryParams : ''}`;
        const res = await fetch(url, { headers: this.getHeaders() });
        return this.handleResponse(res);
    },

    async getTicket(id) {
        const res = await fetch(`${BASE_URL}/tickets/${id}`, { headers: this.getHeaders() });
        return this.handleResponse(res);
    },

    async createTicket(formData) {
        const res = await fetch(`${BASE_URL}/tickets`, {
            method: 'POST',
            headers: this.getHeaders(true),
            body: formData
        });
        return this.handleResponse(res);
    },

    async updateTicketStatus(id, status) {
        const res = await fetch(`${BASE_URL}/tickets/${id}/status`, {
            method: 'PUT',
            headers: this.getHeaders(),
            body: JSON.stringify({ status })
        });
        return this.handleResponse(res);
    },

    async addComment(id, formData) {
        const res = await fetch(`${BASE_URL}/tickets/${id}/comments`, {
            method: 'POST',
            headers: this.getHeaders(true),
            body: formData
        });
        return this.handleResponse(res);
    },

    // Departments
    async getDepartments() {
        const res = await fetch(`${BASE_URL}/tickets/departments`);
        return this.handleResponse(res);
    },

    async getSubDepartments(deptId) {
        if (!deptId) return [];
        const res = await fetch(`${BASE_URL}/tickets/departments/${deptId}/sub_departments`);
        return this.handleResponse(res);
    }
};

// Common utils
const utils = {
    showToast(message, type = 'success') {
        // Find or create toast container
        let toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.className = 'position-fixed bottom-0 end-0 p-3';
            toastContainer.style.zIndex = '11';
            document.body.appendChild(toastContainer);
        }

        const bgColor = type === 'success' ? 'bg-success' : 'bg-danger';
        const toastEl = document.createElement('div');
        toastEl.className = `toast align-items-center text-white ${bgColor} border-0 show`;
        toastEl.setAttribute('role', 'alert');
        toastEl.setAttribute('aria-live', 'assertive');
        toastEl.setAttribute('aria-atomic', 'true');
        
        toastEl.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        toastContainer.appendChild(toastEl);
        
        // Remove toast after 3 seconds
        setTimeout(() => {
            toastEl.classList.remove('show');
            setTimeout(() => toastEl.remove(), 300);
        }, 3000);
    },

    formatDate(dateString) {
        const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
        return new Date(dateString).toLocaleDateString(undefined, options);
    },

    logout() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        window.location.href = 'login.html';
    },
    
    checkAuth() {
        const token = localStorage.getItem('access_token');
        if (!token && !window.location.pathname.includes('login.html') && !window.location.pathname.includes('register.html')) {
            window.location.href = 'login.html';
        }
        return !!token;
    },
    
    getUser() {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    }
};
