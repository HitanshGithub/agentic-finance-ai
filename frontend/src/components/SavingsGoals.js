import { useState, useEffect } from "react";
import { getGoals, createGoal, updateGoal, deleteGoal, getGoalSuggestions } from "../api";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import "./SavingsGoals.css";

function SavingsGoals({ income = 0 }) {
    const [goals, setGoals] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showForm, setShowForm] = useState(false);
    const [newGoal, setNewGoal] = useState({ name: "", target: "", current: "", deadline: "" });
    const [suggestions, setSuggestions] = useState({});
    const [loadingSuggestions, setLoadingSuggestions] = useState({});

    const [editingGoal, setEditingGoal] = useState(null);

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

    // Open Edit Modal
    const handleEditClick = (goal) => {
        setEditingGoal(goal);
    };

    // Save Edited Goal
    const handleSaveEdit = async () => {
        if (!editingGoal.target) {
            alert("Target amount is required");
            return;
        }

        try {
            await updateGoal(editingGoal._id, {
                name: editingGoal.name,
                target: parseFloat(editingGoal.target),
                current: parseFloat(editingGoal.current) || 0,
                deadline: editingGoal.deadline || null
            });
            setEditingGoal(null); // Close modal
            fetchGoals();
        } catch (err) {
            console.error("Error updating goal:", err);
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

            {/* Create Goal Form */}
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
                        placeholder="Target amount (₹)"
                        value={newGoal.target}
                        onChange={(e) => setNewGoal({ ...newGoal, target: e.target.value })}
                    />
                    <input
                        type="number"
                        placeholder="Current savings (₹)"
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
                                        ₹{goal.current?.toLocaleString() || 0} / ₹{goal.target?.toLocaleString() || 0}
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
                                    {/* Edit Button triggers Modal */}
                                    <button onClick={() => handleEditClick(goal)}>
                                        💰 Update / Edit
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
                                        <div className="markdown-content">
                                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                                {suggestions[goal._id]}
                                            </ReactMarkdown>
                                        </div>
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>
            )}

            {/* EDIT MODAL */}
            {editingGoal && (
                <div className="modal-overlay">
                    <div className="modal-content">
                        <h3>✏️ Edit Goal</h3>

                        <label>Goal Name</label>
                        <input
                            type="text"
                            value={editingGoal.name}
                            onChange={(e) => setEditingGoal({ ...editingGoal, name: e.target.value })}
                        />

                        <label>Target Amount (₹)</label>
                        <input
                            type="number"
                            value={editingGoal.target}
                            onChange={(e) => setEditingGoal({ ...editingGoal, target: e.target.value })}
                        />

                        <label>Current Savings (₹)</label>
                        <input
                            type="number"
                            value={editingGoal.current}
                            onChange={(e) => setEditingGoal({ ...editingGoal, current: e.target.value })}
                        />

                        <label>Deadline</label>
                        <input
                            type="date"
                            value={editingGoal.deadline ? editingGoal.deadline.split('T')[0] : ''}
                            onChange={(e) => setEditingGoal({ ...editingGoal, deadline: e.target.value })}
                        />

                        <div className="modal-actions">
                            <button onClick={handleSaveEdit} className="save-btn">💾 Save Changes</button>
                            <button onClick={() => setEditingGoal(null)} className="cancel-btn">❌ Cancel</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default SavingsGoals;
