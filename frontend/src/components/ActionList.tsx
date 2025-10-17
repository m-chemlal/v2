import type { AutomatedAction } from "../types/dashboard";

interface ActionListProps {
  actions: AutomatedAction[];
}

const actionTone: Record<string, string> = {
  blocked: "text-danger",
  emailed: "text-warning",
  logged: "text-gray-400"
};

export function ActionList({ actions }: ActionListProps) {
  return (
    <div className="bg-panel/80 rounded-xl border border-white/5 p-6 h-full">
      <h2 className="text-lg font-semibold mb-4">Automated Actions</h2>
      <div className="space-y-4 text-sm max-h-64 overflow-y-auto pr-1 scrollbar-thin">
        {actions.map((action) => {
          const toneClass = actionTone[action.action_type] ?? "text-gray-300";
          return (
            <div key={action.id} className="flex items-center justify-between">
              <div>
                <p className={`font-medium capitalize ${toneClass}`}>
                  {action.action_type.replace(/_/g, " ")}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  Alert #{action.alert_id} • {new Date(action.executed_at).toLocaleTimeString()}
                </p>
              </div>
            </div>
          );
        })}
        {actions.length === 0 ? <p className="text-sm text-gray-500">No automated responses yet.</p> : null}
      </div>
    </div>
  );
}
