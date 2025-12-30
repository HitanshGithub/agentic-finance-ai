import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";

const COLORS = ["#2563eb", "#22c55e", "#f97316", "#ef4444"];

function ExpensePie({ expenses }) {
  return (
    <ResponsiveContainer width="100%" height={250}>
      <PieChart>
        <Pie
          data={expenses}
          dataKey="amount"
          nameKey="category"
          outerRadius={90}
        >
          {expenses.map((_, i) => (
            <Cell key={i} fill={COLORS[i % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip />
      </PieChart>
    </ResponsiveContainer>
  );
}

export default ExpensePie;
