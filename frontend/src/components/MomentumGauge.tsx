interface MomentumProps {
  sector: string;
  score: number;  // -100 to +100
  signal: string;
  confidence: string;
}

export default function MomentumGauge({ sector, score, signal, confidence }: MomentumProps) {
  const normalized = ((score + 100) / 200) * 100; // 0-100 scale
  const color = score > 30 ? 'text-green-600' : score > -30 ? 'text-yellow-600' : 'text-red-600';
  const barColor = score > 30 ? 'bg-green-500' : score > -30 ? 'bg-yellow-500' : 'bg-red-500';

  return (
    <div className="bg-white rounded-lg shadow-sm border p-4">
      <div className="flex justify-between items-center mb-2">
        <span className="font-semibold text-sm text-brand-deep-teal">{sector}</span>
        <span className={`text-sm font-bold ${color}`}>{signal}</span>
      </div>
      <div className="w-full bg-gray-100 rounded-full h-3 mb-2">
        <div className={`h-3 rounded-full ${barColor} transition-all`} style={{ width: `${normalized}%` }} />
      </div>
      <div className="flex justify-between text-xs text-gray-400">
        <span>Score: {score}</span>
        <span>Confidence: {confidence}</span>
      </div>
    </div>
  );
}
