export default function PredictionsPage() {
  return (
    <div>
      <h2 className="text-2xl font-bold text-brand-deep-teal mb-4">Market Signals & Predictions</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold text-brand-forest mb-2">Sector Momentum</h3>
          <p className="text-sm text-gray-500">Connect to /api/v1/predictions for live momentum scores</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold text-brand-forest mb-2">Pattern Matches</h3>
          <p className="text-sm text-gray-500">Historical pattern matching results will appear here</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold text-brand-forest mb-2">Valuation Zone</h3>
          <p className="text-sm text-gray-500">Nifty PE percentile and expected return range</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold text-brand-forest mb-2">Drawdown Risk</h3>
          <p className="text-sm text-gray-500">Current correction probability estimates</p>
        </div>
      </div>
    </div>
  );
}
