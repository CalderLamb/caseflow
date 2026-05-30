import { useState } from "react";
import { ArrowLeft, FileEdit, ExternalLink, X } from "lucide-react";
import { clsx } from "clsx";
import { useItem, useDraftEstimate, useRequestDraft, useDismissItem, useSnoozeItem } from "../../api/queries";
import { StatePill, ScoreBadge } from "../common/StatePill";
import { CitationChip } from "../common/CitationChip";
import { PredictionBlock } from "./PredictionBlock";

interface Props {
  itemId: string;
  onBack: () => void;
  onDraftReady: (itemId: string, draftId: string) => void;
  onOpenMatter: (id: string) => void;
}

export function ItemDetailView({ itemId, onBack, onDraftReady, onOpenMatter }: Props) {
  const [showEstimate, setShowEstimate] = useState(false);
  const { data: item, isLoading } = useItem(itemId);
  const { data: estimate } = useDraftEstimate(itemId, showEstimate);
  const requestDraft = useRequestDraft();
  const dismiss = useDismissItem();
  const snooze = useSnoozeItem();

  if (isLoading || !item) {
    return (
      <div className="flex items-center justify-center h-full text-neutral-400 text-sm">
        Loading…
      </div>
    );
  }

  const hasDraft = !!item.draft_id;

  const handleRequestDraft = async () => {
    const draft = await requestDraft.mutateAsync(item.id);
    onDraftReady(item.id, draft.id);
  };

  return (
    <div className="max-w-2xl mx-auto px-6 py-6">
      {/* Nav */}
      <button
        onClick={onBack}
        className="flex items-center gap-1 text-xs text-neutral-400 hover:text-neutral-600 mb-5"
      >
        <ArrowLeft size={13} />
        queue
      </button>

      {/* Header */}
      <div className="flex items-start justify-between gap-4 mb-4">
        <div className="min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <StatePill state={item.state} />
            <span className="text-xs text-neutral-400">{item.kind.replace("_", " ")}</span>
            {item.consequence_score !== null && (
              <ScoreBadge score={item.consequence_score} />
            )}
          </div>
          <button
            onClick={() => onOpenMatter(item.matter_id)}
            className="mt-1 text-xs text-neutral-400 hover:text-info flex items-center gap-0.5"
          >
            <ExternalLink size={10} />
            {item.matter_name}
          </button>
        </div>
      </div>

      {/* Trigger */}
      <div className="card px-4 py-4 mb-4">
        <div className="text-xs font-medium text-neutral-500 uppercase tracking-wide mb-2">
          trigger
        </div>
        <p className="text-sm text-neutral-800">{item.trigger_text}</p>
        {item.trigger_citations.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1">
            {item.trigger_citations.map((c, i) => (
              <CitationChip key={i} citation={c} />
            ))}
          </div>
        )}

        {/* Score explainability */}
        {item.score_factors.length > 0 && (
          <div className="mt-3 pt-3 border-t border-neutral-100">
            <div className="text-xs text-neutral-500 mb-1">
              ranked this high because:
            </div>
            <div className="flex flex-wrap gap-1">
              {item.score_factors.map((f, i) => (
                <span
                  key={i}
                  className="text-xs px-1.5 py-0.5 bg-neutral-100 rounded text-neutral-500"
                >
                  {f.label} ({f.weight})
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Assembled facts */}
      {item.assembled_facts.length > 0 && (
        <div className="card px-4 py-4 mb-4">
          <div className="text-xs font-medium text-neutral-500 uppercase tracking-wide mb-2">
            assembled facts
          </div>
          <div className="flex flex-col gap-2">
            {item.assembled_facts.map((f, i) => (
              <div key={i} className="flex items-start gap-2">
                <p className="text-sm text-neutral-700 flex-1">{f.text}</p>
                <CitationChip citation={f.citation} />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Prediction */}
      <div className="mb-4">
        <PredictionBlock
          predictedConfidence={
            estimate ? estimate.predicted_confidence : item.predicted_confidence
          }
          predictedWeaknesses={
            estimate ? estimate.predicted_weaknesses : item.predicted_weaknesses
          }
          estimatedLength={estimate?.estimated_length}
          estimatedTokens={estimate?.estimated_tokens}
        />
      </div>

      {/* Proposed action */}
      {item.proposed_action && (
        <div className="mb-4 text-sm text-neutral-600 bg-neutral-50 rounded-lg px-4 py-3 border border-neutral-200">
          <span className="text-xs text-neutral-400 block mb-1">
            proposed action
          </span>
          {item.proposed_action}
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center gap-2 flex-wrap">
        {!hasDraft && (
          <>
            {!showEstimate && (
              <button
                onClick={() => setShowEstimate(true)}
                className="btn-secondary text-xs"
              >
                see estimate first
              </button>
            )}
            <button
              onClick={handleRequestDraft}
              disabled={requestDraft.isPending}
              className={clsx(
                "btn-primary",
                requestDraft.isPending && "opacity-60 cursor-wait"
              )}
            >
              <FileEdit size={14} />
              {requestDraft.isPending
                ? "generating draft…"
                : estimate
                ? `draft this (~${estimate.estimated_tokens} tokens)`
                : "draft this"}
            </button>
          </>
        )}

        {hasDraft && (
          <button
            onClick={() => onDraftReady(item.id, item.draft_id!)}
            className="btn-primary"
          >
            view draft →
          </button>
        )}

        <div className="flex-1" />

        <button
          onClick={() => dismiss.mutate({ id: item.id, reason: "attorney dismissed" })}
          className="btn text-xs text-neutral-400 hover:text-neutral-600"
        >
          <X size={12} />
          dismiss
        </button>
      </div>

      {requestDraft.isError && (
        <p className="mt-3 text-xs text-critical">
          Draft generation failed — check API key and try again.
        </p>
      )}
    </div>
  );
}
