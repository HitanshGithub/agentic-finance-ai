import { useState, useEffect } from "react";
import { analyzeFinance, getGoals } from "./api";
import { useAuth } from "./AuthContext";
import ExpensePie from "./components/ExpensePie";
import BudgetBar from "./components/BudgetBar";
import PdfUpload from "./components/PdfUpload";
import ResultCard from "./components/ResultCard";
import SavingsGoals from "./components/SavingsGoals";
import ChatAssistant from "./components/ChatAssistant";
import RecurringExpenses from "./components/RecurringExpenses";
import TrendsDashboard from "./components/TrendsDashboard";

function Dashboard() {
  const { user, logout } = useAuth();
  const [income, setIncome] = useState("");
  const [profile, setProfile] = useState("Medium risk");
  const [expenses, setExpenses] = useState([
    { category: "", amount: "" }
  ]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [dark, setDark] = useState(true); // Default to dark mode
  const [activeTab, setActiveTab] = useState("analyze");
  const [goals, setGoals] = useState([]);

  /* 🌙 Dark mode */
  useEffect(() => {
    document.body.className = dark ? "dark" : "";
  }, [dark]);

  /* 📋 Fetch goals for chat context */
  useEffect(() => {
    const fetchGoals = async () => {
      try {
        const data = await getGoals();
        setGoals(data.goals || []);
      } catch (err) {
        console.log("Could not fetch goals");
      }
    };
    fetchGoals();
  }, []);

  /* 💾 Save analysis history */
  useEffect(() => {
    if (result) {
      const history = JSON.parse(localStorage.getItem("history") || "[]");
      // Save result along with input data for full restoration
      const analysisData = {
        ...result,
        expenses: expenses.map(e => ({
          category: e.category,
          amount: Number(e.amount)
        })).filter(e => e.category && e.amount),
        income: Number(income),
        profile: profile,
        savedAt: new Date().toISOString()
      };
      localStorage.setItem("history", JSON.stringify([analysisData, ...history.slice(0, 9)])); // Keep last 10
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
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

  // Prepare expenses for components (filter out empty ones)
  const validExpenses = expenses
    .filter(e => e.category && e.amount)
    .map(e => ({ category: e.category, amount: Number(e.amount) }));

  return (
    <div className="container">
      <header>
        <h1>💰 Smart Finance AI Manager</h1>
        <div className="header-actions">
          {user && (
            <div className="user-info">
              <span className="user-email">
                {user.picture && (
                  <img src={user.picture} alt="" className="user-avatar" />
                )}
                {user.name || user.email}
              </span>
              <button onClick={logout} className="logout-btn">
                Logout
              </button>
            </div>
          )}
          <button onClick={() => setDark(!dark)}>
            {dark ? "☀ Light Mode" : "🌙 Dark Mode"}
          </button>
        </div>
      </header>

      {/* 📑 Navigation Tabs */}
      <nav className="nav-tabs">
        <button
          className={activeTab === "analyze" ? "active" : ""}
          onClick={() => setActiveTab("analyze")}
        >
          📊 Analyze
        </button>
        <button
          className={activeTab === "goals" ? "active" : ""}
          onClick={() => setActiveTab("goals")}
        >
          💎 Goals
        </button>
        <button
          className={activeTab === "recurring" ? "active" : ""}
          onClick={() => setActiveTab("recurring")}
        >
          🔄 Subscriptions
        </button>
        <button
          className={activeTab === "trends" ? "active" : ""}
          onClick={() => setActiveTab("trends")}
        >
          📈 Trends
        </button>
      </nav>

      {/* ===== ANALYZE TAB ===== */}
      <div className="tab-content" style={{ display: activeTab === "analyze" ? "block" : "none" }}>
        {/* 🔢 INPUT SECTION */}
        <div className="form">
          <input
            type="number"
            placeholder="Monthly Income (₹)"
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
                placeholder="Amount (₹)"
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

          <button onClick={analyze} disabled={loading} className="analyze-btn">
            {loading ? "Analyzing..." : "💵 Analyze Finance"}
          </button>

          {history.length > 0 && (
            <button onClick={() => {
              const lastAnalysis = history[0];
              setResult(lastAnalysis);
              // Also restore expenses and income so other tabs work properly
              if (lastAnalysis.expenses && Array.isArray(lastAnalysis.expenses)) {
                setExpenses(lastAnalysis.expenses.map(e => ({
                  category: e.category || '',
                  amount: e.amount?.toString() || ''
                })));
              }
              if (lastAnalysis.income) {
                setIncome(lastAnalysis.income.toString());
              }
              if (lastAnalysis.profile) {
                setProfile(lastAnalysis.profile);
              }
            }}>
              📂 Load Last Analysis
            </button>
          )}
        </div>

        {/* 📊 CHARTS - Only show after analysis */}
        {result && validExpenses.length > 0 && (
          <div className="charts">
            <ExpensePie expenses={validExpenses} />
            <BudgetBar expenses={validExpenses} />
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

      {/* ===== GOALS TAB ===== */}
      <div className="tab-content" style={{ display: activeTab === "goals" ? "block" : "none" }}>
        <SavingsGoals income={Number(income) || 0} />
      </div>

      {/* ===== RECURRING TAB ===== */}
      <div className="tab-content" style={{ display: activeTab === "recurring" ? "block" : "none" }}>
        <RecurringExpenses expenses={validExpenses} />
      </div>

      {/* ===== TRENDS TAB ===== */}
      <div className="tab-content" style={{ display: activeTab === "trends" ? "block" : "none" }}>
        <TrendsDashboard />
      </div>

      {/* 💬 Floating Chat Assistant */}
      <ChatAssistant
        income={Number(income) || 0}
        expenses={validExpenses}
        goals={goals}
      />
    </div>
  );
}

export default Dashboard;
