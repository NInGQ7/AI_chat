// src/api/index.js
import axios from 'axios';

// 确保后端地址正确
const API_BASE_URL = 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  // 移除 Content-Type，让 axios 自动处理 FormData 和 JSON
});

// --- 拦截器 ---
apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

apiClient.interceptors.response.use(
  res => res,
  err => {
    if (err.response && err.response.status === 401) {
      localStorage.removeItem('token');
      if (!window.location.pathname.includes('login')) window.location.reload();
    }
    return Promise.reject(err);
  }
);

export default {
  // ==============================
  // 1. 认证
  // ==============================
  login: (username, password) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    return apiClient.post('/auth/token', formData);
  },

  register: (username, password) => apiClient.post('/auth/register', { username, password }),

  // ==============================
  // 2. 会话管理
  // ==============================
  getSessions: () => apiClient.get('/sessions/'),
  
  createSession: () => apiClient.post('/sessions/'),
  
  // 删除会话 (之前报错缺失的方法)
  deleteSession: (id) => apiClient.delete(`/sessions/${id}`),
  
  // 重命名会话 (PATCH)
  updateSessionTitle: (id, title) => apiClient.patch(`/sessions/${id}`, { title }),
  
  getSessionMessages: (id) => apiClient.get(`/sessions/${id}/messages`),

  // [新增] 上传文件到指定会话 (用于聊天窗口)
  uploadSessionFile: (sessionId, formData) => apiClient.post(`/sessions/${sessionId}/upload`, formData),

  // ==============================
  // 3. 业务功能
  // ==============================
  chat: (payload) => apiClient.post('/chat', payload),
  
  getKnowledgeFiles: () => apiClient.get('/knowledge/files'),

  // [新增] 删除全局文件 (传递 filename 参数)
  deleteKnowledgeFile: (filename) => apiClient.delete(`/knowledge/file`, { params: { filename } }),
  // 全局知识库上传 (用于 KB 页面)
  uploadFile: (formData) => apiClient.post('/upload', formData)
};