const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

class ApiClient {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.defaultHeaders = {
      'Content-Type': 'application/json',
    };
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      ...options,
      headers: {
        ...this.defaultHeaders,
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorData.message || errorMessage;
        } catch (e) {
          // If JSON parsing fails, use the status text
        }
        throw new Error(errorMessage);
      }

      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      }
      
      return await response.text();
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      throw error;
    }
  }

  // Upload endpoints
  async uploadFile(file, onProgress) {
    const formData = new FormData();
    formData.append('files', file);
    formData.append('upload_type', 'zip');

    const xhr = new XMLHttpRequest();
    
    return new Promise((resolve, reject) => {
      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable && onProgress) {
          const progress = (event.loaded / event.total) * 100;
          onProgress(progress);
        }
      });

      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const response = JSON.parse(xhr.responseText);
            resolve(response);
          } catch (error) {
            reject(new Error('Invalid JSON response'));
          }
        } else {
          let errorMessage = `HTTP ${xhr.status}: ${xhr.statusText}`;
          try {
            const errorData = JSON.parse(xhr.responseText);
            errorMessage = errorData.detail?.error || errorData.detail?.details || errorData.detail || errorData.message || errorMessage;
          } catch (error) {
            // If JSON parsing fails, use the status text
          }
          reject(new Error(errorMessage));
        }
      });

      xhr.addEventListener('error', () => {
        reject(new Error('Network error'));
      });

      xhr.open('POST', `${this.baseURL}/api/upload`);
      xhr.send(formData);
    });
  }

  async uploadZip(file, onProgress) {
    return this.uploadFile(file, onProgress);
  }

  // Analysis endpoints
  async analyze(uploadId) {
    return this.request(`/api/analyze?upload_id=${uploadId}`);
  }

  // Planning endpoints
  async plan(uploadId, summary) {
    return this.request('/api/plan', {
      method: 'POST',
      body: JSON.stringify({ upload_id: uploadId, summary }),
    });
  }

  // Agent execution endpoints
  async runAgents(uploadId, plan) {
    return this.request('/api/run', {
      method: 'POST',
      body: JSON.stringify({ upload_id: uploadId, plan }),
    });
  }

  // Clustering endpoints
  async clusterFindings(findings, uploadId) {
    return this.request('/api/cluster', {
      method: 'POST',
      body: JSON.stringify({ 
        findings, 
        upload_id: uploadId,
        clustering_method: 'semantic',
        similarity_threshold: 0.7
      }),
    });
  }

  // Patching endpoints
  async generatePatches(uploadId) {
    return this.request(`/api/patch?upload_id=${uploadId}`, {
      method: 'POST',
    });
  }

  async applyPatches(uploadId, patches) {
    return this.request('/api/apply', {
      method: 'POST',
      body: JSON.stringify({ upload_id: uploadId, patches }),
    });
  }

  // Sandbox endpoints
  async recheckPatches(uploadId) {
    return this.request('/api/recheck', {
      method: 'POST',
      body: JSON.stringify({ upload_id: uploadId }),
    });
  }

  // Report endpoints
  async getReport(uploadId, format = 'html', complianceLevel = 'AA') {
    const response = await fetch(`${this.baseURL}/api/report?upload_id=${uploadId}&format=${format}&compliance_level=${complianceLevel}`);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    if (format === 'json') {
      return await response.json();
    }
    
    return await response.blob();
  }

  async downloadReport(uploadId, format = 'html', complianceLevel = 'AA') {
    const blob = await this.getReport(uploadId, format, complianceLevel);
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `accessibility-report.${format}`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  }

  // Progress WebSocket
  connectProgress(uploadId, onMessage) {
    const ws = new WebSocket(`ws://localhost:8000/api/progress?upload_id=${uploadId}`);
    
    ws.onopen = () => {
      console.log('Progress WebSocket connected');
    };
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (error) {
        console.error('Failed to parse progress message:', error);
      }
    };
    
    ws.onclose = () => {
      console.log('Progress WebSocket disconnected');
    };
    
    ws.onerror = (error) => {
      console.error('Progress WebSocket error:', error);
    };
    
    return ws;
  }

  // Analysis endpoints
  async analyzeUpload(uploadId) {
    return this.request(`/api/analyze?upload_id=${uploadId}`);
  }

  async createPlan(uploadId, analysisResult) {
    return this.request(`/api/plan?upload_id=${uploadId}`, {
      method: 'POST'
    });
  }

  async runAgents(uploadId, plan) {
    return this.request(`/api/run?upload_id=${uploadId}`, {
      method: 'POST'
    });
  }


  // Utility methods
  async healthCheck() {
    try {
      await this.request('/health');
      return true;
    } catch (error) {
      return false;
    }
  }

  async getOpenAPISpec() {
    return this.request('/openapi.json');
  }
}

// Create singleton instance
const apiClient = new ApiClient();

export default apiClient;
