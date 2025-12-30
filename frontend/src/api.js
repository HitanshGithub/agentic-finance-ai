import axios from "axios";

export const analyzeFinance = async (data) => {
  const res = await axios.post(
    "http://127.0.0.1:8000/analyze",
    data,
    { headers: { "Content-Type": "application/json" } }
  );
  return res.data;
};
