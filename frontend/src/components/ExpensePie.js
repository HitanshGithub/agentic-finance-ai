import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from "recharts";

// Green money theme colors
const COLORS = [
  "#10b981", // Primary green
  "#34d399", // Light green  
  "#059669", // Dark green
  "#6ee7b7", // Lighter green
  "#047857", // Deep green
  "#065f46", // Darker green
  "#0d9488", // Teal-green
  "#14b8a6", // Teal
];

// Custom tooltip styling
const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const data = payload[0];
    return (
      <div style={{
        background: 'rgba(26, 31, 42, 0.95)',
        border: '1px solid rgba(16, 185, 129, 0.3)',
        borderRadius: '10px',
        padding: '12px 16px',
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)'
      }}>
        <p style={{ color: data.payload.fill, fontWeight: 600, margin: 0, marginBottom: 4 }}>
          {data.name}
        </p>
        <p style={{ color: '#fff', margin: 0, fontSize: '18px', fontWeight: 700 }}>
          ₹{data.value.toLocaleString()}
        </p>
      </div>
    );
  }
  return null;
};

// Custom legend
const CustomLegend = ({ payload }) => {
  return (
    <div style={{
      display: 'flex',
      flexWrap: 'wrap',
      justifyContent: 'center',
      gap: '12px',
      marginTop: '16px'
    }}>
      {payload.map((entry, index) => (
        <div key={index} style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          fontSize: '12px',
          color: 'rgba(255,255,255,0.7)'
        }}>
          <div style={{
            width: '10px',
            height: '10px',
            borderRadius: '50%',
            backgroundColor: entry.color
          }} />
          {entry.value}
        </div>
      ))}
    </div>
  );
};

function ExpensePie({ expenses }) {
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
        🥧 Expense Distribution
      </h3>
      <ResponsiveContainer width="100%" height={280}>
        <PieChart>
          <Pie
            data={expenses}
            dataKey="amount"
            nameKey="category"
            cx="50%"
            cy="45%"
            outerRadius={90}
            innerRadius={50}
            paddingAngle={3}
            stroke="rgba(0,0,0,0.2)"
            strokeWidth={2}
          >
            {expenses.map((_, i) => (
              <Cell
                key={i}
                fill={COLORS[i % COLORS.length]}
                style={{
                  filter: 'drop-shadow(0 4px 8px rgba(16, 185, 129, 0.3))'
                }}
              />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend content={<CustomLegend />} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}

export default ExpensePie;
