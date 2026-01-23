import { useState, useEffect } from "react";
import { getMonthlyTrends, getCategoryTrends } from "../api";
import "./TrendsDashboard.css";

function TrendsDashboard() {
    const [monthlyData, setMonthlyData] = useState([]);
    const [categoryData, setCategoryData] = useState({});
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState("monthly");

    useEffect(() => {
        fetchTrends();
    }, []);

    const fetchTrends = async () => {
        setLoading(true);
        try {
            const [monthly, categories] = await Promise.all([
                getMonthlyTrends(6),
                getCategoryTrends(6)
            ]);
            setMonthlyData(monthly.trends || []);
            setCategoryData(categories.categories || {});
        } catch (err) {
            console.error("Error fetching trends:", err);
        }
        setLoading(false);
    };

    const getMaxValue = (data, key) => {
        if (!data.length) return 1;
        return Math.max(...data.map(d => d[key] || 0)) || 1;
    };

    const formatMonth = (monthStr) => {
        if (!monthStr) return "";
        const [year, month] = monthStr.split("-");
        const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
        return `${months[parseInt(month) - 1]} ${year.slice(2)}`;
    };

    const totalCategorySpending = Object.values(categoryData).reduce((a, b) => a + b, 0);

    if (loading) {
        return (
            <div className="trends-dashboard">
                <h2>📊 Historical Trends</h2>
                <p className="loading">Loading trends data...</p>
            </div>
        );
    }

    return (
        <div className="trends-dashboard">
            <div className="trends-header">
                <h2>📊 Historical Trends</h2>
                <button onClick={fetchTrends} className="refresh-btn">🔄 Refresh</button>
            </div>

            {/* Tabs */}
            <div className="tabs">
                <button
                    className={activeTab === "monthly" ? "active" : ""}
                    onClick={() => setActiveTab("monthly")}
                >
                    Monthly
                </button>
                <button
                    className={activeTab === "categories" ? "active" : ""}
                    onClick={() => setActiveTab("categories")}
                >
                    Categories
                </button>
            </div>

            {/* Monthly Trends */}
            {activeTab === "monthly" && (
                <div className="monthly-trends">
                    {monthlyData.length === 0 ? (
                        <p className="no-data">No historical data yet. Submit some analyses to see trends!</p>
                    ) : (
                        <>
                            <div className="chart-container">
                                {monthlyData.map((month, i) => {
                                    const maxExpense = getMaxValue(monthlyData, "total_expenses");
                                    const barHeight = (month.total_expenses / maxExpense) * 100;

                                    return (
                                        <div key={i} className="bar-column">
                                            <div className="bar-wrapper">
                                                <div
                                                    className="bar"
                                                    style={{ height: `${barHeight}%` }}
                                                    title={`\u20B9${month.total_expenses.toLocaleString()}`}
                                                >
                                                    <span className="bar-value">₹{month.total_expenses}</span>
                                                </div>
                                            </div>
                                            <span className="bar-label">{formatMonth(month.month)}</span>
                                        </div>
                                    );
                                })}
                            </div>

                            {/* Month-over-month comparison */}
                            {monthlyData.length >= 2 && (
                                <div className="comparison">
                                    {(() => {
                                        const current = monthlyData[monthlyData.length - 1]?.total_expenses || 0;
                                        const previous = monthlyData[monthlyData.length - 2]?.total_expenses || 0;
                                        const diff = current - previous;
                                        const pct = previous ? ((diff / previous) * 100).toFixed(1) : 0;
                                        const isUp = diff > 0;

                                        return (
                                            <div className={`comparison-card ${isUp ? "up" : "down"}`}>
                                                <span className="icon">{isUp ? "📈" : "📉"}</span>
                                                <span className="text">
                                                    You spent {isUp ? `${pct}% more` : `${Math.abs(pct)}% less`} this month
                                                    {isUp ? " — consider reviewing expenses" : " — great job saving!"}
                                                </span>
                                            </div>
                                        );
                                    })()}
                                </div>
                            )}
                        </>
                    )}
                </div>
            )}

            {/* Category Trends */}
            {activeTab === "categories" && (
                <div className="category-trends">
                    {Object.keys(categoryData).length === 0 ? (
                        <p className="no-data">No category data yet.</p>
                    ) : (
                        <div className="category-list">
                            {Object.entries(categoryData).map(([category, amount], i) => {
                                const pct = totalCategorySpending ? (amount / totalCategorySpending) * 100 : 0;

                                return (
                                    <div key={i} className="category-item">
                                        <div className="category-info">
                                            <span className="category-name">{category}</span>
                                            <span className="category-amount">₹{amount.toLocaleString()}</span>
                                        </div>
                                        <div className="category-bar-bg">
                                            <div
                                                className="category-bar"
                                                style={{ width: `${pct}%` }}
                                            />
                                        </div>
                                        <span className="category-pct">{pct.toFixed(1)}%</span>
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

export default TrendsDashboard;
