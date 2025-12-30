import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

function BudgetBar({ expenses }) {
  return (
    <ResponsiveContainer width="100%" height={250}>
      <BarChart data={expenses}>
        <XAxis dataKey="category" />
        <YAxis />
        <Tooltip />
        <Bar dataKey="amount" fill="#2563eb" />
      </BarChart>
    </ResponsiveContainer>
  );
}

export default BudgetBar;
