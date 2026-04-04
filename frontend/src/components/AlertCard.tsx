interface AlertProps {
  priority: string;
  title: string;
  message: string;
  category?: string;
  createdAt?: string;
}

const PRIORITY_CONFIG: Record<string, { emoji: string; border: string; bg: string }> = {
  critical: { emoji: '🔴', border: 'border-red-500', bg: 'bg-red-50' },
  important: { emoji: '🟡', border: 'border-yellow-500', bg: 'bg-yellow-50' },
  info: { emoji: '🔵', border: 'border-blue-500', bg: 'bg-blue-50' },
  client: { emoji: '👤', border: 'border-brand-emerald', bg: 'bg-emerald-50' },
};

export default function AlertCard({ priority, title, message, category, createdAt }: AlertProps) {
  const config = PRIORITY_CONFIG[priority] || PRIORITY_CONFIG.info;

  return (
    <div className={`${config.bg} rounded-lg p-4 border-l-4 ${config.border}`}>
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <span>{config.emoji}</span>
            <span className="font-semibold text-sm text-brand-deep-teal">{title}</span>
            {category && <span className="text-xs bg-white px-2 py-0.5 rounded text-gray-500">{category}</span>}
          </div>
          <p className="text-sm text-gray-600 mt-1 line-clamp-2">{message}</p>
        </div>
        {createdAt && <span className="text-xs text-gray-400 ml-2 whitespace-nowrap">{createdAt}</span>}
      </div>
    </div>
  );
}
