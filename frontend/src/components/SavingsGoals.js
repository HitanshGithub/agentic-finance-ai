import { useState, useEffect } from "react";
import { getGoals, createGoal, updateGoal, deleteGoal, getGoalSuggestions } from "../api";
import "./SavingsGoals.css";

function SavingsGoals({ income = 0 }) {
    const [goals, setGoals] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showForm, setShowForm] = useState(false);
    const [newGoal, setNewGoal] = useState({ name: "", target: "", current: "", deadline: "" });
    const [suggestions, setSuggestions] = useState({});
    const [loadingSuggestions, setLoadingSuggestions] = useState({});

    useEffect(() => {
        fetchGoals();
    }, []);

    const fetchGoals = async () => {
        try {
            const data = await getGoals();
            setGoals(data.goals || []);
        } catch (err) {
            console.error("Error fetching goals:", err);
        }
        setLoading(false);
    };

    const handleCreate = async () => {
        if (!newGoal.name || !newGoal.target) {
            alert("Please enter goal name and target amount");
            return;
        }

        try {
            await createGoal({
                name: newGoal.name,
                target: parseFloat(newGoal.target),
                current: parseFloat(newGoal.current) || 0,
                deadline: newGoal.deadline || null
            });
            setNewGoal({ name: "", target: "", current: "", deadline: "" });
            setShowForm(false);
            fetchGoals();
        } catch (err) {
            console.error("Error creating goal:", err);
        }
    };

    const handleUpdate = async (id, current) => {
        const newAmount = prompt("Enter new current savings amount:", current);
        if (newAmount !== null) {
            try {
                await updateGoal(id, { current: parseFloat(newAmount) });
                fetchGoals();
            } catch (err) {
                console.error("Error updating goal:", err);
            }
        }
    };

    const handleDelete = async (id) => {
        if (window.confirm("Delete this goal?")) {
            try {
                await deleteGoal(id);
                fetchGoals();
            } catch (err) {
                console.error("Error deleting goal:", err);
            }
        }
    };

    const handleGetSuggestions = async (id) => {
        setLoadingSuggestions(prev => ({ ...prev, [id]: true }));
        try {
            const data = await getGoalSuggestions(id, income);
            setSuggestions(prev => ({ ...prev, [id]: data.suggestions }));
        } catch (err) {
            console.error("Error getting suggestions:", err);
        }
        setLoadingSuggestions(prev => ({ ...prev, [id]: false }));
    };

    const calculateProgress = (current, target) => {
        if (!target || target === 0) return 0;
        return Math.min(100, (current / target) * 100);
    };

    if (loading) return <div className="savings-goals"><p>Loading goals...</p></div>;

    return (
        <div className="savings-goals">
            <div className="goals-header">
                <h2>💎 Savings Goals</h2>
                <button onClick={() => setShowForm(!showForm)} className="add-goal-btn">
                    {showForm ? "Cancel" : "+ Add Goal"}
                </button>
            </div>

            {showForm && (
                <div className="goal-form">
                    <input
                        type="text"
                        placeholder="Goal name (e.g., Vacation Fund)"
                        value={newGoal.name}
                        onChange={(e) => setNewGoal({ ...newGoal, name: e.target.value })}
                    />
                    <input
                        type="number"
                        placeholder="Target amount ($)"
                        value={newGoal.target}
                        onChange={(e) => setNewGoal({ ...newGoal, target: e.target.value })}
                    />
                    <input
                        type="number"
                        placeholder="Current savings ($)"
                        value={newGoal.current}
                        onChange={(e) => setNewGoal({ ...newGoal, current: e.target.value })}
                    />
                    <input
                        type="date"
                        placeholder="Deadline"
                        value={newGoal.deadline}
                        onChange={(e) => setNewGoal({ ...newGoal, deadline: e.target.value })}
                    />
                    <button onClick={handleCreate} className="create-btn">Create Goal</button>
                </div>
            )}

            {goals.length === 0 ? (
                <p className="no-goals">No savings goals yet. Create one to get started!</p>
            ) : (
                <div className="goals-list">
                    {goals.map((goal) => {
                        const progress = calculateProgress(goal.current, goal.target);
                        return (
                            <div key={goal._id} className="goal-card">
                                <div className="goal-info">
                                    <h3>{goal.name}</h3>
                                    <p className="goal-amounts">
                                        ${goal.current?.toLocaleString() || 0} / ${goal.target?.toLocaleString() || 0}
                                    </p>
                                    {goal.deadline && (
                                        <p className="goal-deadline">📅 Deadline: {goal.deadline}</p>
                                    )}
                                </div>

                                <div className="progress-bar-container">
                                    <div
                                        className="progress-bar"
                                        style={{ width: `${progress}%` }}
                                    />
                                    <span className="progress-text">{progress.toFixed(1)}%</span>
                                </div>

                                <div className="goal-actions">
                                    <button onClick={() => handleUpdate(goal._id, goal.current)}>
                                        💰 Update
                                    </button>
                                    <button
                                        onClick={() => handleGetSuggestions(goal._id)}
                                        disabled={loadingSuggestions[goal._id]}
                                    >
                                        {loadingSuggestions[goal._id] ? "..." : "💡 Tips"}
                                    </button>
                                    <button onClick={() => handleDelete(goal._id)} className="delete-btn">
                                        🗑️
                                    </button>
                                </div>

                                {suggestions[goal._id] && (
                                    <div className="suggestions-box">
                                        <h4>💡 AI Suggestions:</h4>
                                        <p>{suggestions[goal._id]}</p>
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
}

export default SavingsGoals;
