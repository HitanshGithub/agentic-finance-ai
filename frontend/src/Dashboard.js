import { useState, useEffect } from "react";
import { analyzeFinance } from "./api";
import ExpensePie from "./components/ExpensePie";
import BudgetBar from "./components/BudgetBar";
import PdfUpload from "./components/PdfUpload";
import ResultCard from "./components/ResultCard";

function Dashboard() {
  const [income, setIncome] = useState("");
  const [profile, setProfile] = useState("Medium risk");
  const [expenses, setExpenses] = useState([
    { category: "", amount: "" }
  ]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [dark, setDark] = useState(false);

  /* 🌙 Dark mode */
  useEffect(() => {
    document.body.className = dark ? "dark" : "";
  }, [dark]);

  /* 💾 Save analysis history */
  useEffect(() => {
    if (result) {
      const history = JSON.parse(localStorage.getItem("history") || "[]");
      localStorage.setItem("history", JSON.stringify([result, ...history]));
    }
  }, [result]);

  /* ➕ Add expense */
  const addExpense = () => {
    setExpenses(prev => [...prev, { category: "", amount: "" }]);
  };

  /* ✅ IMMUTABLE update (FIXES read-only error) */
  const updateExpense = (index, field, value) => {
    setExpenses(prev =>
      prev.map((exp, i) =>
        i === index ? { ...exp, [field]: value } : exp
      )
    );
  };

  /* ❌ Remove expense safely */
  const removeExpense = (index) => {
    setExpenses(prev => prev.filter((_, i) => i !== index));
  };

  /* 🤖 Analyze Finance */
  const analyze = async () => {
    setLoading(true);
    setResult(null);

    const payload = {
      income: Number(income),
      profile,
      expenses: expenses.map(e => ({
        category: e.category,
        amount: Number(e.amount)
      }))
    };

    try {
      const res = await analyzeFinance(payload);
      setResult(res);
    } catch {
      alert("Backend not responding");
    }

    setLoading(false);
  };

  const history = JSON.parse(localStorage.getItem("history") || "[]");

  return (
    <div className="container">
      <header>
        <h1>Agentic AI Personal Finance Manager</h1>
        <button onClick={() => setDark(!dark)}>
          {dark ? "☀ Light Mode" : "🌙 Dark Mode"}
        </button>
      </header>

      {/* 🔢 INPUT SECTION */}
      <div className="form">
        <input
          type="number"
          placeholder="Monthly Income"
          value={income}
          onChange={(e) => setIncome(e.target.value)}
        />

        <select value={profile} onChange={(e) => setProfile(e.target.value)}>
          <option>Low risk</option>
          <option>Medium risk</option>
          <option>High risk</option>
        </select>

        <h3>Expenses</h3>
        {Array.isArray(expenses) && expenses.map((exp, i) => (
          <div className="expense-row" key={i}>
            <input
              placeholder="Category"
              value={exp.category}
              onChange={(e) =>
                updateExpense(i, "category", e.target.value)
              }
            />
            <input
              type="number"
              placeholder="Amount"
              value={exp.amount}
              onChange={(e) =>
                updateExpense(i, "amount", e.target.value)
              }
            />
            <button onClick={() => removeExpense(i)}>✖</button>
          </div>
        ))}

        <button onClick={addExpense}>+ Add Expense</button>

        <h3>Upload Bank Statement (PDF)</h3>
        <PdfUpload setExpenses={setExpenses} />

        <button onClick={analyze} disabled={loading}>
          {loading ? "Analyzing..." : "Analyze Finance"}
        </button>

        {history.length > 0 && (
          <button onClick={() => setResult(history[0])}>
            Load Last Analysis
          </button>
        )}
      </div>

      {/* 📊 CHARTS */}
      {Array.isArray(expenses) && expenses.length > 0 && (
        <div className="charts">
          <ExpensePie expenses={expenses} />
          <BudgetBar expenses={expenses} />
        </div>
      )}

      {/* 📄 OUTPUT */}
      {result && (
        <div className="grid">
          <ResultCard title="📊 Expense Analysis" content={result.expense_analysis} />
          <ResultCard title="💰 Budget Plan" content={result.budget_plan} />
          <ResultCard title="📈 Investment Plan" content={result.investment_plan} />
          <ResultCard title="🚨 Fraud Alerts" content={result.fraud_alerts} />
        </div>
      )}
    </div>
  );
}

export default Dashboard;
