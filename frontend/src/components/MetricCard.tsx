import { ReactNode } from "react";

interface MetricCardProps {
  title: string;
  value: ReactNode;
  subtitle?: string;
  tone?: "default" | "success" | "warning" | "danger";
}

const toneToColor: Record<NonNullable<MetricCardProps["tone"]>, string> = {
  default: "text-white",
  success: "text-success",
  warning: "text-warning",
  danger: "text-danger"
};

export function MetricCard({ title, value, subtitle, tone = "default" }: MetricCardProps) {
  return (
    <div className="bg-panel/80 rounded-xl border border-white/5 p-6 backdrop-blur">
      <p className="text-sm uppercase tracking-wide text-gray-400">{title}</p>
      <p className={`text-3xl font-semibold mt-2 ${toneToColor[tone]}`}>{value}</p>
      {subtitle ? <p className="text-xs text-gray-500 mt-2">{subtitle}</p> : null}
    </div>
  );
}
