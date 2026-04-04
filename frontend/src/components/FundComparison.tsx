interface FundData {
  name: string;
  house: string;
  strategy: string;
  returns1y: number;
  returns3y: number;
  returns5y: number;
  maxDrawdown: number;
  sharpe: number;
  feeFixed: number;
  feePerf: number;
}

export default function FundComparison({ fundA, fundB }: { fundA: FundData; fundB: FundData }) {
  const rows: { label: string; a: string; b: string; higherIsBetter?: boolean }[] = [
    { label: 'Fund House', a: fundA.house, b: fundB.house },
    { label: 'Strategy', a: fundA.strategy, b: fundB.strategy },
    { label: '1Y Return', a: `${fundA.returns1y}%`, b: `${fundB.returns1y}%`, higherIsBetter: true },
    { label: '3Y CAGR', a: `${fundA.returns3y}%`, b: `${fundB.returns3y}%`, higherIsBetter: true },
    { label: '5Y CAGR', a: `${fundA.returns5y}%`, b: `${fundB.returns5y}%`, higherIsBetter: true },
    { label: 'Max Drawdown', a: `${fundA.maxDrawdown}%`, b: `${fundB.maxDrawdown}%` },
    { label: 'Sharpe Ratio', a: `${fundA.sharpe}`, b: `${fundB.sharpe}`, higherIsBetter: true },
    { label: 'Fixed Fee', a: `${fundA.feeFixed}%`, b: `${fundB.feeFixed}%` },
    { label: 'Performance Fee', a: `${fundA.feePerf}%`, b: `${fundB.feePerf}%` },
  ];

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="grid grid-cols-3 bg-brand-deep-teal text-white text-sm font-medium">
        <div className="p-3">Metric</div>
        <div className="p-3 text-center">{fundA.name}</div>
        <div className="p-3 text-center">{fundB.name}</div>
      </div>
      {rows.map((row, i) => (
        <div key={i} className={`grid grid-cols-3 text-sm ${i % 2 === 0 ? 'bg-brand-light-bg' : 'bg-white'}`}>
          <div className="p-3 text-gray-600">{row.label}</div>
          <div className="p-3 text-center font-medium">{row.a}</div>
          <div className="p-3 text-center font-medium">{row.b}</div>
        </div>
      ))}
    </div>
  );
}
