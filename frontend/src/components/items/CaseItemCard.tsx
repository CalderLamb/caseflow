import { ChevronRight, FileText, ExternalLink } from "lucide-react";
import { clsx } from "clsx";
import type { CaseItem } from "../../types/api";
import { StatePill, ScoreBadge } from "../common/StatePill";
import { CitationChip } from "../common/CitationChip";

interface Props {
  item: CaseItem;
  onOpen: () => void;
  onOpenMatter: () => void;
}

const KIND_LABELS: Record<string, string> = {
  deadline: "deadline",
  client_update: "client update",
  discovery: "discovery",
  motion_response: "motion response",
  records_request: "records request",
  conflict: "conflict",
  gap: "gap",
  chronology_flag: "chronology flag",
  billing: "billing",
  other: "other",
};

export function CaseItemCard({ item, onOpen, onOpenMatter }: Props) {
  const isCritical = (item.consequence_score ?? 0) >= 70;

  return (
    <div
      className={clsx(
        "card px-4 py-3 cursor-pointer hover:shadow-md transition-shadow group",
        isCritical && "border-critical-border"
      )}
      onClick={onOpen}
    >
      {/* Header row */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2 min-w-0">
          <StatePill state={item.state} />
          <span className="text-xs text-neutral-400">
            {KIND_LABELS[item.kind] ?? item.kind}
          </span>
        </div>
        <div className="flex items-center gap-1.5 shrink-0">
          {item.consequence_score !== null && (
            <ScoreBadge score={item.consequence_score} />
          )}
          <ChevronRight
            size={14}
            className="text-neutral-300 group-hover:text-neutral-500 transition-colors"
          />
        </div>
      </div>

      {/* Matter name */}
      <button
        onClick={(e) => {
          e.stopPropagation();
          onOpenMatter();
        }}
        className="mt-1 text-xs text-neutral-400 hover:text-info hover:underline flex items-center gap-0.5"
      >
        <ExternalLink size={10} />
        {item.matter_name.length > 55
          ? item.matter_name.slice(0, 55) + "…"
          : item.matter_name}
      </button>

      {/* Trigger text */}
      <p className="mt-2 text-sm text-neutral-700 leading-snug">
        {item.trigger_text}
      </p>

      {/* Citations */}
      {item.trigger_citations.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1">
          {item.trigger_citations.slice(0, 3).map((c, i) => (
            <CitationChip key={i} citation={c} />
          ))}
        </div>
      )}

      {/* Score factors — shown on high-score items */}
      {isCritical && item.score_factors.length > 0 && (
        <p className="mt-2 text-xs text-critical/80">
          critical because:{" "}
          {item.score_factors
            .slice(0, 3)
            .map((f) => f.label)
            .join(", ")}
        </p>
      )}

      {/* Footer */}
      <div className="mt-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          {item.predicted_confidence && (
            <span className="text-xs text-neutral-400">
              predicted{" "}
              <span
                className={clsx(
                  "font-medium",
                  item.predicted_confidence === "high"
                    ? "text-green-600"
                    : item.predicted_confidence === "medium"
                    ? "text-warning"
                    : "text-critical"
                )}
              >
                {item.predicted_confidence}
              </span>{" "}
              draft
            </span>
          )}
        </div>
        {item.review_slot && (
          <span className="text-xs text-neutral-400">
            review scheduled
          </span>
        )}
        {item.state === "drafted" && (
          <span className="text-xs text-info font-medium">
            draft ready →
          </span>
        )}
      </div>
    </div>
  );
}
