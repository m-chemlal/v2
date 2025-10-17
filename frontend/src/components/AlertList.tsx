import type { Alert } from "../types/dashboard";

const severityStyles: Record<Alert["severity"], string> = {
  critical: "bg-danger/20 text-danger",
  high: "bg-danger/10 text-danger",
  medium: "bg-warning/20 text-warning",
  low: "bg-success/20 text-success"
};

interface AlertListProps {
  alerts: Alert[];
}

export function AlertList({ alerts }: AlertListProps) {
  return (
    <div className="bg-panel/80 rounded-xl border border-white/5 p-6 h-full">
      <h2 className="text-lg font-semibold mb-4">Real-Time Alerts</h2>
      <div className="space-y-4 max-h-64 overflow-y-auto pr-1 scrollbar-thin">
        {alerts.map((alert) => (
          <div key={alert.id} className="flex items-start justify-between">
            <div>
              <p className="font-medium">{alert.summary}</p>
              <p className="text-xs text-gray-500 mt-1">
                Score {alert.score.toFixed(2)} • {new Date(alert.created_at).toLocaleTimeString()}
              </p>
            </div>
            <span className={`px-3 py-1 rounded-full text-xs font-semibold ${severityStyles[alert.severity]}`}>
              {alert.severity.toUpperCase()}
            </span>
          </div>
        ))}
        {alerts.length === 0 ? <p className="text-sm text-gray-500">No alerts yet.</p> : null}
      </div>
    </div>
  );
}
