import { useState } from "react";
import { RefreshCw } from "lucide-react";
import { useQueue, useMatters } from "../../api/queries";
import { QueueHeader } from "./QueueHeader";
import { QueueStats } from "./QueueStats";
import { QueueSection } from "./QueueSection";
import type { CaseItem } from "../../types/api";

interface Props {
  onOpenItem: (id: string) => void;
  onOpenMatter: (id: string) => void;
}

export function QueueView({ onOpenItem, onOpenMatter }: Props) {
  const [filterMatter, setFilterMatter] = useState<string | undefined>();
  const { data, isLoading, error, refetch } = useQueue({
    matter_id: filterMatter,
  });
  const { data: matters } = useMatters();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full text-neutral-400 text-sm gap-2">
        <RefreshCw size={14} className="animate-spin" />
        Loading queue…
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 text-sm text-critical">
        Failed to load queue — backend may be starting up.{" "}
        <button onClick={() => refetch()} className="underline">
          Retry
        </button>
      </div>
    );
  }

  const items = data?.items ?? [];

  const critical = items.filter(
    (i) => (i.consequence_score ?? 0) >= 70 && i.state !== "done"
  );
  const drafted = items.filter((i) =>
    ["drafted", "draft_requested"].includes(i.state)
  );
  const rest = items.filter(
    (i) =>
      !critical.includes(i) &&
      !drafted.includes(i) &&
      !["done", "dismissed", "snoozed"].includes(i.state)
  );

  return (
    <div className="max-w-3xl mx-auto px-6 py-6">
      <QueueHeader
        total={data?.total ?? 0}
        matters={matters ?? []}
        filterMatter={filterMatter}
        onFilterMatter={setFilterMatter}
        onRefresh={refetch}
      />
      <QueueStats items={items} />

      <div className="mt-6 flex flex-col gap-6">
        {critical.length > 0 && (
          <QueueSection
            label="critical"
            labelColor="critical"
            items={critical}
            onOpenItem={onOpenItem}
            onOpenMatter={onOpenMatter}
          />
        )}
        {drafted.length > 0 && (
          <QueueSection
            label="draft ready"
            labelColor="info"
            items={drafted}
            onOpenItem={onOpenItem}
            onOpenMatter={onOpenMatter}
          />
        )}
        {rest.length > 0 && (
          <QueueSection
            label="detected"
            labelColor="neutral"
            items={rest}
            onOpenItem={onOpenItem}
            onOpenMatter={onOpenMatter}
          />
        )}
        {items.length === 0 && (
          <div className="text-center py-16 text-neutral-400 text-sm">
            Queue is empty — all items reviewed.
          </div>
        )}
      </div>
    </div>
  );
}
