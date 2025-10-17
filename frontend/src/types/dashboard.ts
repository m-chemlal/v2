export type Severity = "critical" | "high" | "medium" | "low";

export interface DashboardSummary {
  vulnerabilities_detected: number;
  high_count: number;
  medium_count: number;
  low_count: number;
  ai_insights: {
    top_signals: string[];
    model_version: string;
  };
  recent_scans: Scan[];
  latest_alerts: Alert[];
  automated_actions: AutomatedAction[];
}

export interface Scan {
  id: number;
  asset_id: number;
  command: string;
  started_at: string;
  ended_at: string | null;
  parsed_result?: {
    ports?: Array<{
      port: number;
      protocol: string;
      state: string;
      service: string;
    }>;
  };
}

export interface Alert {
  id: number;
  asset_id: number | null;
  summary: string;
  severity: Severity;
  score: number;
  created_at: string;
  details?: Record<string, unknown>;
}

export interface AutomatedAction {
  id: number;
  alert_id: number;
  action_type: string;
  executed_at: string;
  details?: Record<string, unknown>;
}
