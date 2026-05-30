import { RefreshCw, ChevronDown } from "lucide-react";
import { format } from "date-fns";
import type { Matter } from "../../types/api";

interface Props {
  total: number;
  matters: Matter[];
  filterMatter: string | undefined;
  onFilterMatter: (id: string | undefined) => void;
  onRefresh: () => void;
}

export function QueueHeader({
  total,
  matters,
  filterMatter,
  onFilterMatter,
  onRefresh,
}: Props) {
  const today = format(new Date(), "EEEE, MMMM d");
  const activeMatter = matters.find((m) => m.id === filterMatter);

  return (
    <div className="flex items-start justify-between mb-4">
      <div>
        <h1 className="text-xl font-medium text-neutral-800">
          {activeMatter ? activeMatter.name : "all matters"}
        </h1>
        <p className="text-xs text-neutral-400 mt-0.5">
          {today} · {total} item{total !== 1 ? "s" : ""} open
        </p>
      </div>

      <div className="flex items-center gap-2">
        <select
          value={filterMatter ?? ""}
          onChange={(e) =>
            onFilterMatter(e.target.value || undefined)
          }
          className="text-sm border border-neutral-200 rounded-md px-2 py-1.5 bg-white text-neutral-600 appearance-none pr-6"
        >
          <option value="">all matters</option>
          {matters.map((m) => (
            <option key={m.id} value={m.id}>
              {m.name.length > 40 ? m.name.slice(0, 40) + "…" : m.name}
            </option>
          ))}
        </select>
        <button
          onClick={onRefresh}
          className="p-1.5 rounded-md text-neutral-400 hover:text-neutral-600 hover:bg-neutral-100"
          title="Refresh"
        >
          <RefreshCw size={14} />
        </button>
      </div>
    </div>
  );
}
