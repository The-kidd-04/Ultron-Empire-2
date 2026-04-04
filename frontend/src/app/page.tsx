export default function Dashboard() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-brand-deep-teal">Dashboard</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <DashCard title="Total AUM" value="₹12 Cr" subtitle="Across 3 clients" color="emerald" />
        <DashCard title="Active Alerts" value="2" subtitle="1 critical, 1 important" color="red" />
        <DashCard title="Nifty 50" value="24,150" subtitle="+0.85%" color="green" />
        <DashCard title="India VIX" value="13.2" subtitle="Low volatility" color="blue" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-brand-deep-teal mb-4">Recent Alerts</h3>
          <p className="text-gray-500 text-sm">Connect to /api/v1/alerts for live data</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-brand-deep-teal mb-4">Client Reviews Due</h3>
          <p className="text-gray-500 text-sm">Connect to /api/v1/clients for live data</p>
        </div>
      </div>
    </div>
  );
}

function DashCard({ title, value, subtitle, color }: { title: string; value: string; subtitle: string; color: string }) {
  const colorMap: Record<string, string> = {
    emerald: 'border-brand-emerald',
    red: 'border-red-500',
    green: 'border-green-500',
    blue: 'border-blue-500',
  };
  return (
    <div className={`bg-white rounded-lg shadow p-5 border-l-4 ${colorMap[color] || 'border-gray-300'}`}>
      <p className="text-sm text-gray-500">{title}</p>
      <p className="text-2xl font-bold text-brand-deep-teal mt-1">{value}</p>
      <p className="text-xs text-gray-400 mt-1">{subtitle}</p>
    </div>
  );
}
