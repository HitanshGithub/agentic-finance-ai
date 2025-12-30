function ExpenseRow({ expense, index, updateExpense, removeExpense }) {
  return (
    <div className="expense-row">
      <input
        type="text"
        placeholder="Category"
        value={expense.category}
        onChange={(e) =>
          updateExpense(index, "category", e.target.value)
        }
      />
      <input
        type="number"
        placeholder="Amount"
        value={expense.amount}
        onChange={(e) =>
          updateExpense(index, "amount", e.target.value)
        }
      />
      <button onClick={() => removeExpense(index)}>✖</button>
    </div>
  );
}

export default ExpenseRow;
