import type { Scan } from "../types/dashboard";

interface ScanListProps {
  scans: Scan[];
}

export function ScanList({ scans }: ScanListProps) {
  return (
    <div className="bg-panel/80 rounded-xl border border-white/5 p-6 h-full">
      <h2 className="text-lg font-semibold mb-4">Recent Scans</h2>
      <div className="space-y-4 text-sm max-h-64 overflow-y-auto pr-1 scrollbar-thin">
        {scans.map((scan) => (
          <div key={scan.id} className="flex items-center justify-between">
            <div>
              <p className="font-medium text-gray-100">{scan.command}</p>
              <p className="text-xs text-gray-500 mt-1">
                {new Date(scan.started_at).toLocaleTimeString()} • Ports scanned: {scan.parsed_result?.ports?.length ?? "n/a"}
              </p>
            </div>
            <span className="text-xs text-gray-400">
              #{scan.id.toString().padStart(3, "0")}
            </span>
          </div>
        ))}
        {scans.length === 0 ? <p className="text-sm text-gray-500">No scans recorded yet.</p> : null}
      </div>
    </div>
  );
}
