import { clsx } from "clsx";
import type { CaseItem } from "../../types/api";
import { CaseItemCard } from "../items/CaseItemCard";

interface Props {
  label: string;
  labelColor: "critical" | "info" | "neutral";
  items: CaseItem[];
  onOpenItem: (id: string) => void;
  onOpenMatter: (id: string) => void;
}

const LABEL_COLORS = {
  critical: "text-critical",
  info: "text-info",
  neutral: "text-neutral-400",
};

export function QueueSection({
  label,
  labelColor,
  items,
  onOpenItem,
  onOpenMatter,
}: Props) {
  return (
    <div>
      <div className="flex items-center gap-2 mb-2">
        <span
          className={clsx(
            "text-xs font-medium uppercase tracking-wide",
            LABEL_COLORS[labelColor]
          )}
        >
          {label}
        </span>
        <span className="text-xs text-neutral-400">({items.length})</span>
      </div>
      <div className="flex flex-col gap-2">
        {items.map((item) => (
          <CaseItemCard
            key={item.id}
            item={item}
            onOpen={() => onOpenItem(item.id)}
            onOpenMatter={() => onOpenMatter(item.matter_id)}
          />
        ))}
      </div>
    </div>
  );
}
