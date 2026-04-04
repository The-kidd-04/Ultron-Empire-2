'use client';

interface Holding {
  product: string;
  amount: number;
}

const COLORS = ['#008C6F', '#003235', '#63D2B7', '#10645C', '#D3D3D3', '#1A1A1A'];

export default function PortfolioChart({ holdings }: { holdings: Holding[] }) {
  const total = holdings.reduce((s, h) => s + h.amount, 0);

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="font-semibold text-brand-deep-teal mb-4">Portfolio Allocation</h3>
      <div className="space-y-3">
        {holdings.map((h, i) => {
          const pct = (h.amount / total) * 100;
          return (
            <div key={i}>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-700">{h.product}</span>
                <span className="font-medium">₹{h.amount} Cr ({pct.toFixed(0)}%)</span>
              </div>
              <div className="w-full bg-gray-100 rounded-full h-2">
                <div className="h-2 rounded-full" style={{ width: `${pct}%`, backgroundColor: COLORS[i % COLORS.length] }} />
              </div>
            </div>
          );
        })}
      </div>
      <div className="mt-4 pt-3 border-t text-sm font-bold text-brand-deep-teal">
        Total: ₹{total} Cr
      </div>
    </div>
  );
}
