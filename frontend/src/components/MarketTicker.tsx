interface TickerItem {
  name: string;
  value: string;
  change: number;
}

export default function MarketTicker({ items }: { items: TickerItem[] }) {
  return (
    <div className="bg-brand-deep-teal text-white overflow-hidden">
      <div className="flex gap-8 px-4 py-2 text-xs animate-marquee whitespace-nowrap">
        {items.map((item, i) => (
          <span key={i} className="inline-flex gap-1">
            <span className="opacity-70">{item.name}</span>
            <span className="font-medium">{item.value}</span>
            <span className={item.change >= 0 ? 'text-green-400' : 'text-red-400'}>
              {item.change >= 0 ? '▲' : '▼'} {Math.abs(item.change).toFixed(2)}%
            </span>
          </span>
        ))}
      </div>
    </div>
  );
}
