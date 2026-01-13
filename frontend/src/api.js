import axios from "axios";

const API_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000";

export const analyzeFinance = async (data) => {
  const res = await axios.post(
    `${API_URL}/analyze`,
    data,
    { headers: { "Content-Type": "application/json" } }
  );
  return res.data;
};
