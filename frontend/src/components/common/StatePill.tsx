import { clsx } from "clsx";
import type { ItemState, Confidence } from "../../types/api";

const STATE_STYLES: Record<ItemState, string> = {
  detected: "bg-neutral-100 text-neutral-500",
  evaluated: "bg-neutral-100 text-neutral-600",
  draft_requested: "bg-info-light text-info border border-info-border",
  drafted: "bg-info-light text-info border border-info-border",
  scheduled: "bg-green-50 text-green-700 border border-green-200",
  reviewed: "bg-green-50 text-green-700 border border-green-200",
  done: "bg-neutral-100 text-neutral-400",
  dismissed: "bg-neutral-100 text-neutral-400",
  snoozed: "bg-neutral-100 text-neutral-400",
};

const STATE_LABELS: Record<ItemState, string> = {
  detected: "detected",
  evaluated: "evaluated",
  draft_requested: "draft requested",
  drafted: "draft ready",
  scheduled: "scheduled",
  reviewed: "reviewed",
  done: "done",
  dismissed: "dismissed",
  snoozed: "snoozed",
};

export function StatePill({ state }: { state: ItemState }) {
  return (
    <span
      className={clsx(
        "pill text-[11px]",
        STATE_STYLES[state] ?? "bg-neutral-100 text-neutral-500"
      )}
    >
      {STATE_LABELS[state] ?? state}
    </span>
  );
}

const CONFIDENCE_STYLES: Record<Confidence, string> = {
  high: "bg-green-50 text-green-700 border border-green-200",
  medium: "bg-warning-light text-warning border border-warning-border",
  low: "bg-critical-light text-critical border border-critical-border",
};

export function ConfidencePill({ confidence }: { confidence: Confidence }) {
  return (
    <span className={clsx("pill text-[11px]", CONFIDENCE_STYLES[confidence])}>
      {confidence} confidence
    </span>
  );
}

export function ScoreBadge({ score }: { score: number }) {
  const color =
    score >= 80
      ? "bg-critical-light text-critical border border-critical-border"
      : score >= 50
      ? "bg-warning-light text-warning border border-warning-border"
      : "bg-neutral-100 text-neutral-500";

  return (
    <span className={clsx("pill text-[11px] tabular-nums", color)}>
      {Math.round(score)}
    </span>
  );
}
