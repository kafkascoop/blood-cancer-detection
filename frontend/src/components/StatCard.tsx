import { Card } from 'primereact/card';
import type { LucideIcon } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  color: 'blue' | 'emerald' | 'amber' | 'rose' | 'purple';
  subtitle?: string;
  trend?: { value: number; positive: boolean };
}

const colorMap = {
  blue: { bg: 'bg-blue-50', icon: 'text-blue-600' },
  emerald: { bg: 'bg-emerald-50', icon: 'text-emerald-600' },
  amber: { bg: 'bg-amber-50', icon: 'text-amber-600' },
  rose: { bg: 'bg-rose-50', icon: 'text-rose-600' },
  purple: { bg: 'bg-purple-50', icon: 'text-purple-600' },
};

export default function StatCard({ title, value, icon: Icon, color, subtitle, trend }: StatCardProps) {
  const c = colorMap[color];

  return (
    <Card className="shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between mb-4">
        <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${c.bg} ${c.icon}`}>
          <Icon size={22} />
        </div>
        {trend && (
          <span className={`text-xs font-semibold px-1.5 py-0.5 rounded-full ${trend.positive ? 'bg-emerald-50 text-emerald-600' : 'bg-rose-50 text-rose-600'}`}>
            {trend.positive ? '↑' : '↓'} {Math.abs(trend.value)}%
          </span>
        )}
      </div>
      <div className="flex flex-col">
        <span className="text-xs font-medium text-gray-500 uppercase tracking-wider">{title}</span>
        <span className="text-2xl font-bold mt-1">{value}</span>
        {subtitle && <span className="text-xs text-gray-400 mt-1">{subtitle}</span>}
      </div>
    </Card>
  );
}
