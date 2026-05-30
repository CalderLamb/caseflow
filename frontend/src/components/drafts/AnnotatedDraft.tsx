import { useState } from "react";
import { clsx } from "clsx";
import type { Annotation, WeaknessCategory } from "../../types/api";

const CATEGORY_STYLES: Record<WeaknessCategory, string> = {
  law: "bg-red-100 border-b-2 border-critical cursor-pointer",
  facts: "bg-amber-100 border-b-2 border-warning cursor-pointer",
  data: "bg-blue-100 border-b-2 border-info cursor-pointer",
  contradiction: "bg-purple-100 border-b-2 border-purple-500 cursor-pointer",
  procedure: "bg-emerald-100 border-b-2 border-emerald-500 cursor-pointer",
};

const NOTE_BORDER: Record<WeaknessCategory, string> = {
  law: "border-critical-border bg-critical-light text-red-800",
  facts: "border-warning-border bg-warning-light text-yellow-800",
  data: "border-info-border bg-info-light text-blue-800",
  contradiction: "border-purple-200 bg-purple-50 text-purple-800",
  procedure: "border-emerald-200 bg-emerald-50 text-emerald-800",
};

interface Props {
  body: string;
  annotations: Annotation[];
  isEditing: boolean;
  editedBody: string;
  onEditChange: (v: string) => void;
}

export function AnnotatedDraft({ body, annotations, isEditing, editedBody, onEditChange }: Props) {
  const [activeAnnotation, setActiveAnnotation] = useState<number | null>(null);

  if (isEditing) {
    return (
      <textarea
        value={editedBody}
        onChange={(e) => onEditChange(e.target.value)}
        className="w-full min-h-[400px] p-4 text-sm font-mono text-neutral-800 border border-neutral-200 rounded-lg resize-y focus:outline-none focus:ring-1 focus:ring-neutral-400"
      />
    );
  }

  // Build annotated spans
  const sorted = [...annotations].sort((a, b) => a.span_start - b.span_start);
  const segments: React.ReactNode[] = [];
  let cursor = 0;

  sorted.forEach((ann, idx) => {
    if (ann.span_start > cursor) {
      segments.push(
        <span key={`text-${idx}`}>{body.slice(cursor, ann.span_start)}</span>
      );
    }
    const spanText = body.slice(ann.span_start, Math.min(ann.span_end, body.length));
    segments.push(
      <span
        key={`ann-${idx}`}
        className={clsx("rounded-sm px-0.5", CATEGORY_STYLES[ann.category])}
        onClick={() =>
          setActiveAnnotation(activeAnnotation === idx ? null : idx)
        }
      >
        {spanText}
        {activeAnnotation === idx && (
          <span
            className={clsx(
              "absolute z-10 mt-1 ml-0 w-72 px-3 py-2 rounded-lg border text-xs shadow-md",
              NOTE_BORDER[ann.category]
            )}
            style={{ display: "block", position: "absolute" }}
          >
            <span className="font-medium block mb-0.5">{ann.category}</span>
            {ann.note}
          </span>
        )}
      </span>
    );
    cursor = Math.min(ann.span_end, body.length);
  });

  if (cursor < body.length) {
    segments.push(<span key="tail">{body.slice(cursor)}</span>);
  }

  if (annotations.length === 0) {
    return (
      <pre className="text-sm text-neutral-800 whitespace-pre-wrap font-sans leading-relaxed">
        {body}
      </pre>
    );
  }

  return (
    <div className="relative">
      <pre className="text-sm text-neutral-800 whitespace-pre-wrap font-sans leading-relaxed relative">
        {segments}
      </pre>
      {activeAnnotation !== null && sorted[activeAnnotation] && (
        <div
          className={clsx(
            "mt-3 px-3 py-2.5 rounded-lg border text-xs",
            NOTE_BORDER[sorted[activeAnnotation].category]
          )}
        >
          <span className="font-medium">{sorted[activeAnnotation].category}</span>
          <span className="ml-2">{sorted[activeAnnotation].note}</span>
        </div>
      )}
    </div>
  );
}
