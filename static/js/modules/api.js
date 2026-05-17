export const API_BASE = `${window.location.origin}/api/admin`;

export async function apiFetch(endpoint, options = {}) {
    const adminKey = localStorage.getItem('adminKey') || '';
    const headers = {
        'Authorization': `Bearer ${adminKey}`,
        'Content-Type': 'application/json',
        ...(options.headers || {})
    };

    const response = await fetch(`${API_BASE}${endpoint}`, { ...options, headers });
    
    if (response.status === 401) {
        window.dispatchEvent(new CustomEvent('auth-failed'));
        return null;
    }

    return response;
}
