import { useState, useEffect } from "react";
import { detectRecurring } from "../api";
import "./RecurringExpenses.css";

function RecurringExpenses({ expenses = [] }) {
    const [recurring, setRecurring] = useState([]);
    const [totals, setTotals] = useState({ monthly: 0, annual: 0 });
    const [suggestions, setSuggestions] = useState([]);
    const [loading, setLoading] = useState(false);
    const [analyzed, setAnalyzed] = useState(false);

    const handleAnalyze = async () => {
        if (expenses.length === 0) {
            alert("No expenses to analyze. Please add expenses first.");
            return;
        }

        setLoading(true);
        try {
            const data = await detectRecurring(expenses);
            setRecurring(data.recurring || []);
            setTotals({
                monthly: data.total_monthly || 0,
                annual: data.total_annual || 0
            });
            setSuggestions(data.suggestions || []);
            setAnalyzed(true);
        } catch (err) {
            console.error("Error detecting recurring expenses:", err);
        }
        setLoading(false);
    };

    // Auto-analyze when expenses change
    useEffect(() => {
        // Reset state when expenses change
        setAnalyzed(false);
        setRecurring([]);
        setTotals({ monthly: 0, annual: 0 });
        setSuggestions([]);

        // Auto-analyze if there are valid expenses
        if (expenses.length > 0) {
            const timer = setTimeout(() => {
                handleAnalyze();
            }, 100);
            return () => clearTimeout(timer);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [JSON.stringify(expenses)]);

    return (
        <div className="recurring-expenses">
            <div className="recurring-header">
                <h2>🔄 Recurring Expenses</h2>
                <button onClick={handleAnalyze} disabled={loading} className="analyze-btn">
                    {loading ? "Analyzing..." : "🔍 Analyze"}
                </button>
            </div>

            {!analyzed && !loading && (
                <p className="no-data">Click "Analyze" to detect recurring expenses from your data.</p>
            )}

            {analyzed && recurring.length === 0 && (
                <p className="no-data">No recurring expenses detected.</p>
            )}

            {recurring.length > 0 && (
                <>
                    {/* Summary Cards */}
                    <div className="summary-cards">
                        <div className="summary-card monthly">
                            <span className="label">Monthly Total</span>
                            <span className="value">${totals.monthly.toLocaleString()}</span>
                        </div>
                        <div className="summary-card annual">
                            <span className="label">Annual Total</span>
                            <span className="value">${totals.annual.toLocaleString()}</span>
                        </div>
                    </div>

                    {/* Suggestions */}
                    {suggestions.length > 0 && (
                        <div className="suggestions">
                            {suggestions.map((suggestion, i) => (
                                <div key={i} className="suggestion-item">
                                    💡 {suggestion}
                                </div>
                            ))}
                        </div>
                    )}

                    {/* Recurring Items List */}
                    <div className="recurring-list">
                        {recurring.map((item, i) => (
                            <div key={i} className="recurring-item">
                                <div className="item-info">
                                    <span className="item-name">{item.category}</span>
                                    <span className="item-frequency">{item.frequency}</span>
                                </div>
                                <div className="item-amounts">
                                    <span className="monthly-amount">${item.amount}/mo</span>
                                    <span className="annual-amount">${item.annual_cost}/yr</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </>
            )}
        </div>
    );
}

export default RecurringExpenses;
