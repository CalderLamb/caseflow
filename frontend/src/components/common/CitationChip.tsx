import { FileText, Mail, Calendar } from "lucide-react";
import type { Citation } from "../../types/api";

const KIND_ICON = {
  document: FileText,
  email: Mail,
  event: Calendar,
};

export function CitationChip({ citation }: { citation: Citation }) {
  const Icon = KIND_ICON[citation.kind as keyof typeof KIND_ICON] ?? FileText;
  return (
    <span className="inline-flex items-center gap-1 px-1.5 py-0.5 bg-neutral-100 rounded text-[11px] text-neutral-500 border border-neutral-200">
      <Icon size={10} />
      {citation.label}
      {citation.page !== undefined && (
        <span className="text-neutral-400"> p.{citation.page}</span>
      )}
    </span>
  );
}
