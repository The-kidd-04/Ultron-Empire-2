interface ClientProps {
  id: number;
  name: string;
  city: string;
  riskProfile: string;
  aumCr: number;
  tags: string[];
  nextReview?: string;
}

const RISK_COLORS: Record<string, string> = {
  Aggressive: 'bg-red-100 text-red-700',
  Moderate: 'bg-yellow-100 text-yellow-700',
  Conservative: 'bg-green-100 text-green-700',
};

export default function ClientCard({ id, name, city, riskProfile, aumCr, tags, nextReview }: ClientProps) {
  return (
    <div className="bg-white rounded-lg shadow-sm border p-4 hover:shadow-md transition">
      <div className="flex justify-between items-start">
        <div>
          <a href={`/clients/${id}`} className="font-semibold text-brand-deep-teal hover:text-brand-emerald">
            {name}
          </a>
          <p className="text-xs text-gray-500 mt-0.5">{city}</p>
        </div>
        <span className={`text-xs px-2 py-1 rounded-full font-medium ${RISK_COLORS[riskProfile] || 'bg-gray-100'}`}>
          {riskProfile}
        </span>
      </div>
      <div className="mt-3 flex justify-between items-end">
        <div>
          <p className="text-xs text-gray-400">AUM with us</p>
          <p className="text-lg font-bold text-brand-deep-teal">₹{aumCr} Cr</p>
        </div>
        {nextReview && (
          <p className="text-xs text-gray-400">Review: {nextReview}</p>
        )}
      </div>
      {tags.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1">
          {tags.map((t) => (
            <span key={t} className="text-[10px] bg-brand-mint/20 text-brand-forest px-2 py-0.5 rounded">{t}</span>
          ))}
        </div>
      )}
    </div>
  );
}
