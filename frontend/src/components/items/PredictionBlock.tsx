import { clsx } from "clsx";
import type { Confidence, PredictedWeakness } from "../../types/api";

const WEAKNESS_COLORS: Record<string, string> = {
  law: "text-critical bg-critical-light border-critical-border",
  facts: "text-warning bg-warning-light border-warning-border",
  data: "text-info bg-info-light border-info-border",
  contradiction: "text-purple-700 bg-purple-50 border-purple-200",
  procedure: "text-emerald-700 bg-emerald-50 border-emerald-200",
};

const CONFIDENCE_RING: Record<Confidence, string> = {
  high: "border-green-400 bg-green-50",
  medium: "border-warning bg-warning-light",
  low: "border-critical bg-critical-light",
};

const CONFIDENCE_TEXT: Record<Confidence, string> = {
  high: "text-green-700",
  medium: "text-warning",
  low: "text-critical",
};

interface Props {
  predictedConfidence: Confidence | null;
  predictedWeaknesses: PredictedWeakness[];
  estimatedLength?: string;
  estimatedTokens?: number;
}

export function PredictionBlock({
  predictedConfidence,
  predictedWeaknesses,
  estimatedLength,
  estimatedTokens,
}: Props) {
  if (!predictedConfidence) return null;

  return (
    <div className="card px-4 py-4">
      <div className="text-xs font-medium text-neutral-500 uppercase tracking-wide mb-3">
        draft prediction
      </div>

      <div className="flex items-center gap-3">
        <div
          className={clsx(
            "w-10 h-10 rounded-full border-2 flex items-center justify-center shrink-0",
            CONFIDENCE_RING[predictedConfidence]
          )}
        >
          <span
            className={clsx(
              "text-sm font-medium",
              CONFIDENCE_TEXT[predictedConfidence]
            )}
          >
            {predictedConfidence[0].toUpperCase()}
          </span>
        </div>
        <div>
          <div className="text-sm font-medium text-neutral-700">
            likely{" "}
            <span className={CONFIDENCE_TEXT[predictedConfidence]}>
              {predictedConfidence}
            </span>{" "}
            confidence
          </div>
          {(estimatedLength || estimatedTokens) && (
            <div className="text-xs text-neutral-400 mt-0.5">
              {estimatedLength}
              {estimatedTokens && ` · ~${estimatedTokens} tokens`}
            </div>
          )}
        </div>
      </div>

      {predictedWeaknesses.length > 0 && (
        <div className="mt-3 flex flex-col gap-1.5">
          {predictedWeaknesses.map((w, i) => (
            <div
              key={i}
              className={clsx(
                "flex items-start gap-2 px-2.5 py-2 rounded-md border text-xs",
                WEAKNESS_COLORS[w.category] ?? "text-neutral-600 bg-neutral-50 border-neutral-200"
              )}
            >
              <span className="font-medium shrink-0">{w.category}</span>
              <span className="opacity-80">{w.note}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
