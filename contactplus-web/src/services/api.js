import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Health check
export const checkHealth = () => api.get('/health');

// Contact operations
export const getContacts = (page = 1, pageSize = 50, activeOnly = true) => 
  api.get('/contacts', { params: { page, page_size: pageSize, active_only: activeOnly } });

export const getContact = (contactId) => api.get(`/contacts/${contactId}`);

export const searchContacts = (query, fields = ['fn', 'email', 'phone', 'organization'], page = 1, pageSize = 50) =>
  api.get('/contacts/search', { params: { query, fields, page, page_size: pageSize } });

export const updateContact = (contactId, data) => api.put(`/contacts/${contactId}`, data);

export const deleteContact = (contactId) => api.delete(`/contacts/${contactId}`);

// Import/Export operations
export const importInitialDatabases = () => api.post('/import/initial');

export const getImportStatus = () => api.get('/import/status');

export const exportDatabase = (activeOnly = true) => {
  return axios({
    url: `${API_BASE_URL}/export/vcf`,
    method: 'GET',
    params: { active_only: activeOnly },
    responseType: 'blob',
  });
};

// System operations
export const getDatabaseStats = () => api.get('/stats');

export default api;