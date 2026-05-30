import { ArrowLeft, FileText, AlertCircle, Calendar, BookOpen } from "lucide-react";
import { format, parseISO } from "date-fns";
import { useMatter } from "../api/queries";
import { ScoreBadge, StatePill } from "../components/common/StatePill";

interface Props {
  matterId: string;
  onBack: () => void;
  onOpenItem: (id: string) => void;
}

export function MatterView({ matterId, onBack, onOpenItem }: Props) {
  const { data: matter, isLoading } = useMatter(matterId);

  if (isLoading || !matter) {
    return (
      <div className="flex items-center justify-center h-full text-neutral-400 text-sm">
        Loading matter…
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-6 py-6">
      <button
        onClick={onBack}
        className="flex items-center gap-1 text-xs text-neutral-400 hover:text-neutral-600 mb-5"
      >
        <ArrowLeft size={13} />
        queue
      </button>

      {/* Header */}
      <div className="mb-6">
        <h1 className="text-xl font-medium text-neutral-800">{matter.name}</h1>
        <div className="flex items-center gap-3 mt-1 text-xs text-neutral-400">
          <span>{matter.client_name}</span>
          {matter.case_number && <span>· {matter.case_number}</span>}
          {matter.court && <span>· {matter.court}</span>}
          {matter.sol_date && (
            <span className="text-critical font-medium">
              · SOL {matter.sol_date}
            </span>
          )}
        </div>
        <div className="mt-2 text-xs text-neutral-400">
          {matter.total_token_cost.toLocaleString()} tokens used on this matter
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Case items */}
        <section className="col-span-2">
          <SectionHeader icon={<AlertCircle size={13} />} label={`open items (${matter.open_item_count})`} />
          <div className="flex flex-col gap-1.5">
            {matter.items
              .filter((i) => !["done", "dismissed"].includes(i.state))
              .map((i) => (
                <button
                  key={i.id}
                  onClick={() => onOpenItem(i.id)}
                  className="text-left card px-3 py-2.5 hover:shadow-sm transition-shadow"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-neutral-700 leading-snug line-clamp-2">
                      {i.trigger_text}
                    </span>
                    <div className="flex items-center gap-1.5 ml-2 shrink-0">
                      <StatePill state={i.state as never} />
                      {i.consequence_score !== undefined && (
                        <ScoreBadge score={i.consequence_score} />
                      )}
                    </div>
                  </div>
                </button>
              ))}
            {matter.items.length === 0 && (
              <p className="text-xs text-neutral-400">no open items</p>
            )}
          </div>
        </section>

        {/* Deadlines */}
        <section>
          <SectionHeader icon={<Calendar size={13} />} label={`deadlines (${matter.deadlines.length})`} />
          <div className="flex flex-col gap-1">
            {matter.deadlines.map((d) => (
              <div
                key={d.id}
                className="text-xs px-2.5 py-2 rounded-md bg-white border border-neutral-200"
              >
                <div className={d.is_malpractice_class ? "text-critical font-medium" : "text-neutral-700"}>
                  {d.description}
                </div>
                <div className="text-neutral-400 mt-0.5">{d.due_date}</div>
              </div>
            ))}
            {matter.deadlines.length === 0 && (
              <p className="text-xs text-neutral-400">none detected</p>
            )}
          </div>
        </section>

        {/* Documents */}
        <section>
          <SectionHeader icon={<FileText size={13} />} label={`documents (${matter.documents.length})`} />
          <div className="flex flex-col gap-1">
            {matter.documents.slice(0, 10).map((d) => (
              <div
                key={d.id}
                className="flex items-center gap-2 text-xs px-2.5 py-1.5 rounded-md bg-white border border-neutral-200"
              >
                <span className="text-neutral-700 truncate flex-1">{d.title}</span>
                {d.doc_type && (
                  <span className="text-neutral-400 shrink-0">{d.doc_type}</span>
                )}
                {!d.processed && (
                  <span className="text-warning shrink-0">processing</span>
                )}
              </div>
            ))}
            {matter.documents.length === 0 && (
              <p className="text-xs text-neutral-400">no documents ingested yet</p>
            )}
          </div>
        </section>

        {/* Chronology */}
        {matter.chronology.length > 0 && (
          <section className="col-span-2">
            <SectionHeader icon={<BookOpen size={13} />} label={`chronology (${matter.chronology.length} entries)`} />
            <div className="flex flex-col gap-1">
              {matter.chronology.slice(0, 15).map((e) => (
                <div
                  key={e.id}
                  className={`text-xs px-2.5 py-2 rounded-md border ${
                    e.flagged
                      ? "bg-warning-light border-warning-border"
                      : "bg-white border-neutral-200"
                  }`}
                >
                  <div className="flex items-center gap-2">
                    {e.date_of_entry && (
                      <span className="text-neutral-400 shrink-0">{e.date_of_entry}</span>
                    )}
                    {e.provider && (
                      <span className="font-medium text-neutral-700">{e.provider}</span>
                    )}
                    {e.flagged && (
                      <span className="text-warning font-medium">⚠ flagged</span>
                    )}
                  </div>
                  {e.findings && (
                    <p className="text-neutral-600 mt-0.5">{e.findings}</p>
                  )}
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Facts */}
        {matter.facts.length > 0 && (
          <section className="col-span-2">
            <SectionHeader icon={<BookOpen size={13} />} label={`assembled facts (${matter.facts.length})`} />
            <div className="flex flex-col gap-1">
              {matter.facts.slice(0, 10).map((f) => (
                <div key={f.id} className="text-xs px-2.5 py-2 rounded-md bg-white border border-neutral-200">
                  <span className="text-neutral-700">{f.text}</span>
                  {f.issue_tags && f.issue_tags.length > 0 && (
                    <div className="flex gap-1 mt-1">
                      {f.issue_tags.map((t) => (
                        <span key={t} className="px-1.5 py-0.5 bg-neutral-100 rounded text-neutral-400">
                          {t}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </section>
        )}
      </div>
    </div>
  );
}

function SectionHeader({ icon, label }: { icon: React.ReactNode; label: string }) {
  return (
    <div className="flex items-center gap-1.5 text-xs font-medium text-neutral-500 uppercase tracking-wide mb-2">
      <span className="text-neutral-400">{icon}</span>
      {label}
    </div>
  );
}
