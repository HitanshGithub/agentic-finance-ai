import axios from "axios";

const API_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000";

// Create axios instance with interceptors
const api = axios.create({
  baseURL: API_URL,
  headers: { "Content-Type": "application/json" }
});

// Add auth token to all requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 errors (token expired)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('token');
      // Redirect to login if not already there
      if (window.location.pathname !== '/login' && window.location.pathname !== '/signup') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);


// ===== AUTHENTICATION =====

export const signup = async (email, password) => {
  const res = await api.post('/auth/signup', { email, password });
  return res.data;
};

export const login = async (email, password) => {
  const res = await api.post('/auth/login', { email, password });
  return res.data;
};

export const googleLogin = async (token) => {
  const res = await api.post('/auth/google', { token });
  return res.data;
};

export const verifyEmail = async (token) => {
  const res = await api.get(`/auth/verify/${token}`);
  return res.data;
};

export const getCurrentUser = async () => {
  const res = await api.get('/auth/me');
  return res.data;
};


// ===== FINANCE ANALYSIS =====

export const analyzeFinance = async (data) => {
  const res = await api.post('/analyze', data);
  return res.data;
};

export const getHistory = async (limit = 10) => {
  const res = await api.get(`/history?limit=${limit}`);
  return res.data;
};

export const getAnalysisById = async (id) => {
  const res = await api.get(`/history/${id}`);
  return res.data;
};


// ===== SAVINGS GOALS =====

export const createGoal = async (data) => {
  const res = await api.post('/goals', data);
  return res.data;
};

export const getGoals = async () => {
  const res = await api.get('/goals');
  return res.data;
};

export const updateGoal = async (id, data) => {
  const res = await api.put(`/goals/${id}`, data);
  return res.data;
};

export const deleteGoal = async (id) => {
  const res = await api.delete(`/goals/${id}`);
  return res.data;
};

export const getGoalSuggestions = async (id, income = 0) => {
  const res = await api.get(`/goals/${id}/suggestions?income=${income}`);
  return res.data;
};


// ===== AI CHAT =====

export const sendChatMessage = async (message, context = {}) => {
  const res = await api.post('/chat', { message, context });
  return res.data;
};

export const getChatHistory = async (limit = 50) => {
  const res = await api.get(`/chat/history?limit=${limit}`);
  return res.data;
};

export const clearChat = async () => {
  const res = await api.post('/chat/clear');
  return res.data;
};


// ===== RECURRING EXPENSES =====

export const detectRecurring = async (expenses) => {
  const res = await api.post('/detect-recurring', { expenses });
  return res.data;
};


// ===== TRENDS =====

export const getMonthlyTrends = async (months = 6) => {
  const res = await api.get(`/trends/monthly?months=${months}`);
  return res.data;
};

export const getCategoryTrends = async (months = 6) => {
  const res = await api.get(`/trends/categories?months=${months}`);
  return res.data;
};
