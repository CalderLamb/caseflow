import type { WeaknessCategory } from "../../types/api";

const LEGEND: { category: WeaknessCategory; color: string; label: string }[] = [
  { category: "law", color: "bg-critical", label: "law — citation may be wrong/outdated" },
  { category: "facts", color: "bg-warning", label: "facts — assertion thinly sourced" },
  { category: "data", color: "bg-info", label: "data — assumes something not in file" },
  { category: "contradiction", color: "bg-purple-500", label: "contradiction — internal inconsistency" },
  { category: "procedure", color: "bg-emerald-500", label: "procedure — format/required element" },
];

export function WeaknessLegend({ activeCategories }: { activeCategories: WeaknessCategory[] }) {
  if (activeCategories.length === 0) return null;
  const active = LEGEND.filter((l) => activeCategories.includes(l.category));

  return (
    <div className="flex flex-wrap gap-2 py-2">
      {active.map((l) => (
        <div key={l.category} className="flex items-center gap-1.5 text-xs text-neutral-500">
          <span className={`w-2 h-2 rounded-full ${l.color}`} />
          {l.label}
        </div>
      ))}
    </div>
  );
}
