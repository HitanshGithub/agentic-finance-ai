# Agentic AI Personal Finance Manager 💸🤖

An end-to-end **Agentic AI system** that analyzes personal finances using multiple AI agents.

## 🔥 Features
- Expense analysis
- Budget planning
- Investment suggestions
- Fraud detection
- Bank PDF upload & parsing
- Interactive charts (Pie & Bar)
- Markdown-rendered AI output
- Dark mode
- History tracking

## 🧠 Architecture
- Frontend: React.js
- Backend: FastAPI
- AI Model: Gemma (Google Generative AI)
- Agents: Expense, Budget, Investment, Fraud

## 🚀 How to Run

### Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
