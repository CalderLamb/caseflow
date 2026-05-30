import { useState } from "react";
import { ArrowLeft, Edit2, Check, X, ChevronDown } from "lucide-react";
import { clsx } from "clsx";
import { useDraft, useItem, useApproveDraft, usePatchDraft } from "../../api/queries";
import { ConfidenceBanner } from "./ConfidenceBanner";
import { WeaknessLegend } from "./WeaknessLegend";
import { AnnotatedDraft } from "./AnnotatedDraft";
import type { WeaknessCategory } from "../../types/api";

interface Props {
  itemId: string;
  draftId: string;
  onBack: () => void;
  onApproved: () => void;
}

export function DraftReviewView({ itemId, draftId, onBack, onApproved }: Props) {
  const [isEditing, setIsEditing] = useState(false);
  const [editedBody, setEditedBody] = useState("");
  const [lowConfExpanded, setLowConfExpanded] = useState(false);

  const { data: draft, isLoading: draftLoading } = useDraft(draftId);
  const { data: item } = useItem(itemId);
  const approve = useApproveDraft();
  const patch = usePatchDraft();

  if (draftLoading || !draft) {
    return (
      <div className="flex items-center justify-center h-full text-neutral-400 text-sm">
        Loading draft…
      </div>
    );
  }

  const activeCategories = [
    ...new Set(draft.annotations.map((a) => a.category as WeaknessCategory)),
  ];

  const isLowConf = draft.confidence === "low" && !lowConfExpanded;

  const handleSaveEdit = async () => {
    await patch.mutateAsync({ id: draft.id, body: editedBody });
    setIsEditing(false);
  };

  const handleApprove = async () => {
    await approve.mutateAsync(draft.id);
    onApproved();
  };

  return (
    <div className="max-w-2xl mx-auto px-6 py-6">
      {/* Nav */}
      <button
        onClick={onBack}
        className="flex items-center gap-1 text-xs text-neutral-400 hover:text-neutral-600 mb-5"
      >
        <ArrowLeft size={13} />
        {item?.matter_name ?? "item"}
      </button>

      {/* Title */}
      <div className="mb-4">
        <h1 className="text-lg font-medium text-neutral-800">
          draft — {item?.kind?.replace("_", " ")}
        </h1>
        {item && (
          <p className="text-xs text-neutral-400 mt-0.5">{item.matter_name}</p>
        )}
      </div>

      {/* CONFIDENCE BANNER — always first, always visible */}
      <div className="mb-3">
        <ConfidenceBanner
          confidence={draft.confidence}
          isCollapsed={isLowConf}
          onExpand={() => setLowConfExpanded(true)}
        />
      </div>

      {/* Token cost */}
      <div className="mb-3 text-xs text-neutral-400">
        {draft.token_cost.toLocaleString()} tokens used
        {draft.status === "edited" && " · edited"}
      </div>

      {/* Weakness legend */}
      {activeCategories.length > 0 && !isLowConf && (
        <div className="mb-3">
          <WeaknessLegend activeCategories={activeCategories} />
        </div>
      )}

      {/* Draft body */}
      {!isLowConf && (
        <div className="card px-5 py-5 mb-4">
          <AnnotatedDraft
            body={draft.body}
            annotations={draft.annotations}
            isEditing={isEditing}
            editedBody={editedBody || draft.body}
            onEditChange={setEditedBody}
          />
        </div>
      )}

      {/* Actions */}
      {!isLowConf && (
        <div className="flex items-center gap-2 flex-wrap">
          {isEditing ? (
            <>
              <button
                onClick={handleSaveEdit}
                disabled={patch.isPending}
                className="btn-primary"
              >
                <Check size={14} />
                {patch.isPending ? "saving…" : "save edits"}
              </button>
              <button
                onClick={() => setIsEditing(false)}
                className="btn-secondary"
              >
                <X size={14} />
                cancel
              </button>
            </>
          ) : (
            <>
              <button
                onClick={() => {
                  setEditedBody(draft.body);
                  setIsEditing(true);
                }}
                className="btn-secondary"
              >
                <Edit2 size={14} />
                edit
              </button>
              <button
                onClick={handleApprove}
                disabled={approve.isPending}
                className={clsx(
                  "btn-primary",
                  approve.isPending && "opacity-60 cursor-wait"
                )}
              >
                <Check size={14} />
                {approve.isPending ? "approving…" : "approve"}
              </button>
            </>
          )}
        </div>
      )}
    </div>
  );
}
