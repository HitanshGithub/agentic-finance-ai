import axios from "axios";

const API_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000";

// ===== FINANCE ANALYSIS =====

export const analyzeFinance = async (data) => {
  const res = await axios.post(
    `${API_URL}/analyze`,
    data,
    { headers: { "Content-Type": "application/json" } }
  );
  return res.data;
};

export const getHistory = async (limit = 10) => {
  const res = await axios.get(`${API_URL}/history?limit=${limit}`);
  return res.data;
};

export const getAnalysisById = async (id) => {
  const res = await axios.get(`${API_URL}/history/${id}`);
  return res.data;
};


// ===== SAVINGS GOALS =====

export const createGoal = async (data) => {
  const res = await axios.post(
    `${API_URL}/goals`,
    data,
    { headers: { "Content-Type": "application/json" } }
  );
  return res.data;
};

export const getGoals = async () => {
  const res = await axios.get(`${API_URL}/goals`);
  return res.data;
};

export const updateGoal = async (id, data) => {
  const res = await axios.put(
    `${API_URL}/goals/${id}`,
    data,
    { headers: { "Content-Type": "application/json" } }
  );
  return res.data;
};

export const deleteGoal = async (id) => {
  const res = await axios.delete(`${API_URL}/goals/${id}`);
  return res.data;
};

export const getGoalSuggestions = async (id, income = 0) => {
  const res = await axios.get(`${API_URL}/goals/${id}/suggestions?income=${income}`);
  return res.data;
};


// ===== AI CHAT =====

export const sendChatMessage = async (message, context = {}) => {
  const res = await axios.post(
    `${API_URL}/chat`,
    { message, context },
    { headers: { "Content-Type": "application/json" } }
  );
  return res.data;
};

export const clearChat = async () => {
  const res = await axios.post(`${API_URL}/chat/clear`);
  return res.data;
};


// ===== RECURRING EXPENSES =====

export const detectRecurring = async (expenses) => {
  const res = await axios.post(
    `${API_URL}/detect-recurring`,
    { expenses },
    { headers: { "Content-Type": "application/json" } }
  );
  return res.data;
};


// ===== TRENDS =====

export const getMonthlyTrends = async (months = 6) => {
  const res = await axios.get(`${API_URL}/trends/monthly?months=${months}`);
  return res.data;
};

export const getCategoryTrends = async (months = 6) => {
  const res = await axios.get(`${API_URL}/trends/categories?months=${months}`);
  return res.data;
};
