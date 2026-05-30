import type { CaseItem } from "../../types/api";

export function QueueStats({ items }: { items: CaseItem[] }) {
  const critical = items.filter((i) => (i.consequence_score ?? 0) >= 70).length;
  const draftReady = items.filter((i) => i.state === "drafted").length;
  const scheduled = items.filter((i) => i.state === "scheduled").length;
  const total = items.length;

  return (
    <div className="grid grid-cols-4 gap-3">
      <StatCard label="total open" value={total} />
      <StatCard label="critical" value={critical} color="critical" />
      <StatCard label="draft ready" value={draftReady} color="info" />
      <StatCard label="scheduled" value={scheduled} color="neutral" />
    </div>
  );
}

function StatCard({
  label,
  value,
  color = "neutral",
}: {
  label: string;
  value: number;
  color?: "critical" | "info" | "neutral";
}) {
  const valueColor =
    color === "critical"
      ? "text-critical"
      : color === "info"
      ? "text-info"
      : "text-neutral-700";

  return (
    <div className="card px-3 py-2.5">
      <div className={`text-lg font-medium tabular-nums ${valueColor}`}>
        {value}
      </div>
      <div className="text-xs text-neutral-400 mt-0.5">{label}</div>
    </div>
  );
}
