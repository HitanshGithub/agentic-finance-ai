import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";

// Green money theme gradient colors
const COLORS = [
  "#10b981", // Primary green
  "#059669", // Dark green
  "#34d399", // Light green
  "#6ee7b7", // Lighter green
  "#047857", // Deep green
  "#065f46", // Darker green
];

// Custom tooltip styling
const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div style={{
        background: 'rgba(26, 31, 42, 0.95)',
        border: '1px solid rgba(16, 185, 129, 0.3)',
        borderRadius: '10px',
        padding: '12px 16px',
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)'
      }}>
        <p style={{ color: '#10b981', fontWeight: 600, margin: 0, marginBottom: 4 }}>
          {label}
        </p>
        <p style={{ color: '#fff', margin: 0, fontSize: '18px', fontWeight: 700 }}>
          ₹{payload[0].value.toLocaleString()}
        </p>
      </div>
    );
  }
  return null;
};

function BudgetBar({ expenses }) {
  return (
    <div style={{
      background: 'linear-gradient(145deg, #1a1f2a 0%, #0c0f14 100%)',
      borderRadius: '20px',
      padding: '24px',
      border: '1px solid rgba(16, 185, 129, 0.1)'
    }}>
      <h3 style={{
        color: '#10b981',
        margin: '0 0 20px 0',
        fontSize: '16px',
        fontWeight: 600,
        display: 'flex',
        alignItems: 'center',
        gap: '8px'
      }}>
        📊 Expense Breakdown
      </h3>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={expenses} margin={{ top: 10, right: 10, left: -10, bottom: 10 }}>
          <XAxis
            dataKey="category"
            tick={{ fill: 'rgba(255,255,255,0.6)', fontSize: 12 }}
            axisLine={{ stroke: 'rgba(255,255,255,0.1)' }}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: 'rgba(255,255,255,0.6)', fontSize: 12 }}
            axisLine={{ stroke: 'rgba(255,255,255,0.1)' }}
            tickLine={false}
            tickFormatter={(value) => `₹${value}`}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(16, 185, 129, 0.1)' }} />
          <Bar dataKey="amount" radius={[8, 8, 0, 0]}>
            {expenses.map((_, index) => (
              <Cell
                key={`cell-${index}`}
                fill={COLORS[index % COLORS.length]}
                style={{
                  filter: 'drop-shadow(0 4px 8px rgba(16, 185, 129, 0.3))'
                }}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default BudgetBar;
