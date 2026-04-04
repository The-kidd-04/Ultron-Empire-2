interface SectorData {
  name: string;
  changePct: number;
}

export default function SectorHeatmap({ sectors }: { sectors: SectorData[] }) {
  const getColor = (change: number) => {
    if (change > 2) return 'bg-green-600 text-white';
    if (change > 0.5) return 'bg-green-400 text-white';
    if (change > -0.5) return 'bg-gray-200 text-gray-700';
    if (change > -2) return 'bg-red-400 text-white';
    return 'bg-red-600 text-white';
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="font-semibold text-brand-deep-teal mb-4">Sector Heatmap</h3>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        {sectors.map((s) => (
          <div key={s.name} className={`${getColor(s.changePct)} rounded-lg p-3 text-center`}>
            <div className="text-xs font-medium">{s.name}</div>
            <div className="text-lg font-bold">{s.changePct >= 0 ? '+' : ''}{s.changePct.toFixed(1)}%</div>
          </div>
        ))}
      </div>
    </div>
  );
}
