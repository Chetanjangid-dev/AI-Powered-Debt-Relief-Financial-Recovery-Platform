const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

async function request(endpoint, options = {}) {
  const token = localStorage.getItem('auth_token')
  const headers = {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options.headers,
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  })

  const data = await response.json().catch(() => null)

  if (!response.ok) {
    throw new Error(data?.detail || data?.message || 'Request failed')
  }

  return data
}

export const api = {
  auth: {
    login: (credentials) =>
      request('/api/auth/login', { method: 'POST', body: JSON.stringify(credentials) }),
    register: (userData) =>
      request('/api/auth/register', { method: 'POST', body: JSON.stringify(userData) }),
  },

  dashboard: {
    getOverview: () => request('/api/dashboard'),
  },

  settlement: {
    predict: (payload) =>
      request('/api/settlement/predict', { method: 'POST', body: JSON.stringify(payload) }),
  },

  negotiation: {
    generate: (payload) =>
      request('/api/negotiation/generate', { method: 'POST', body: JSON.stringify(payload) }),
  },

  rights: {
    getAll: () => request('/api/rights'),
  },

  history: {
    getAll: () => request('/api/history'),
  },
}

export default api
