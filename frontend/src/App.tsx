import { Header } from "./components/Header";
import { MetricCard } from "./components/MetricCard";
import { AiInsights } from "./components/AiInsights";
import { AlertList } from "./components/AlertList";
import { ScanList } from "./components/ScanList";
import { ActionList } from "./components/ActionList";
import { useDashboardData } from "./hooks/useDashboardData";

const version = __APP_VERSION__;

function LoadingState() {
  return (
    <div className="flex items-center justify-center h-[70vh] text-gray-400">
      Loading Trusted AI SOC Lite…
    </div>
  );
}

function ErrorState({ message }: { message: string }) {
  return (
    <div className="flex items-center justify-center h-[70vh] text-danger">
      {message}
    </div>
  );
}

export default function App() {
  const { data, loading, error } = useDashboardData();

  if (loading) {
    return (
      <div className="min-h-screen bg-background text-white px-10 py-12">
        <Header title="TRUSTED AI SOC LITE" version={version} />
        <LoadingState />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-background text-white px-10 py-12">
        <Header title="TRUSTED AI SOC LITE" version={version} />
        <ErrorState message={error ?? "No data available"} />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background text-white px-10 py-12">
      <Header title="TRUSTED AI SOC LITE" version={version} />

      <div className="grid gap-6 grid-cols-1 lg:grid-cols-4">
        <MetricCard
          title="Vulnerabilities Detected"
          value={data.vulnerabilities_detected}
          subtitle={`${data.high_count} High • ${data.medium_count} Medium • ${data.low_count} Low`}
          tone={data.high_count > 0 ? "danger" : "default"}
        />
        <MetricCard
          title="High Severity"
          value={data.high_count}
          tone="danger"
        />
        <MetricCard
          title="Medium Severity"
          value={data.medium_count}
          tone="warning"
        />
        <MetricCard
          title="Low Severity"
          value={data.low_count}
          tone="success"
        />
      </div>

      <div className="grid gap-6 grid-cols-1 lg:grid-cols-3 mt-6">
        <div className="lg:col-span-2 grid gap-6 grid-cols-1 md:grid-cols-2">
          <AlertList alerts={data.latest_alerts} />
          <ScanList scans={data.recent_scans} />
        </div>
        <AiInsights topSignals={data.ai_insights.top_signals} modelVersion={data.ai_insights.model_version} />
      </div>

      <div className="grid gap-6 grid-cols-1 lg:grid-cols-2 mt-6">
        <ActionList actions={data.automated_actions} />
        <div className="bg-panel/80 rounded-xl border border-white/5 p-6">
          <h2 className="text-lg font-semibold mb-3">Audit Log Snapshot</h2>
          <p className="text-sm text-gray-400">
            Every AI decision is recorded with feature importance scores and playbook actions.
            Access the JSON lines in <code className="bg-black/30 px-1 py-0.5 rounded">/data/audit</code> for full details.
          </p>
        </div>
      </div>
    </div>
  );
}
