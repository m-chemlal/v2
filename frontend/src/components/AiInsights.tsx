interface AiInsightsProps {
  topSignals: string[];
  modelVersion: string;
}

export function AiInsights({ topSignals, modelVersion }: AiInsightsProps) {
  return (
    <div className="bg-panel/80 rounded-xl border border-white/5 p-6 h-full">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">AI Analysis</h2>
        <span className="text-xs text-gray-500">Model {modelVersion}</span>
      </div>
      <div className="space-y-3">
        {topSignals.map((signal, index) => (
          <div key={signal} className="bg-accentMuted/40 rounded-lg p-3 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="text-xs text-gray-400">{String(index + 1).padStart(2, "0")}</span>
              <span className="font-medium text-gray-100 capitalize">{signal.replace(/_/g, " ")}</span>
            </div>
            <span className="text-accent text-sm font-semibold">SHAP</span>
          </div>
        ))}
        {topSignals.length === 0 ? <p className="text-sm text-gray-500">No AI explanations available.</p> : null}
      </div>
    </div>
  );
}
