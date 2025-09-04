import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// API endpoints
export const api = {
  // Health check
  health: () => apiClient.get('/healthz'),
  
  // File upload
  uploadFiles: (files: File[]) => {
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });
    return apiClient.post('/upload/files', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  // Pipeline execution
  runPipeline: (data: any) => apiClient.post('/pipeline/run', data),
  
  // Report generation
  generatePDFReport: (sessionId: string) => 
    apiClient.get(`/report/pdf?session_id=${sessionId}`, {
      responseType: 'blob',
    }),
  
  // Export patched files
  exportPatchedFiles: (sessionId: string) =>
    apiClient.get(`/export/zip?session_id=${sessionId}`, {
      responseType: 'blob',
    }),
  
  // Configuration
  getModelMap: () => apiClient.get('/config/model-map'),
  updateModelMap: (modelMap: any) => apiClient.post('/config/model-map', modelMap),
  
  // Session management
  getSessionFiles: (sessionId: string) => apiClient.get(`/sessions/${sessionId}/files`),
  clearSession: (sessionId: string) => apiClient.delete(`/sessions/${sessionId}`),
};

export default apiClient;
