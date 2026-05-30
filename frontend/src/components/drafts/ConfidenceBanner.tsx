import { clsx } from "clsx";
import { AlertTriangle, CheckCircle, AlertCircle } from "lucide-react";
import type { Confidence } from "../../types/api";

const STYLES: Record<Confidence, { bg: string; text: string; icon: React.ReactNode; label: string }> = {
  high: {
    bg: "bg-green-50 border-green-200",
    text: "text-green-800",
    icon: <CheckCircle size={15} />,
    label: "high confidence — all facts cited, authorities verified",
  },
  medium: {
    bg: "bg-warning-light border-warning-border",
    text: "text-yellow-800",
    icon: <AlertTriangle size={15} />,
    label: "medium confidence — some authorities unverified or data gaps noted",
  },
  low: {
    bg: "bg-critical-light border-critical-border",
    text: "text-red-800",
    icon: <AlertCircle size={15} />,
    label: "low confidence — unverifiable propositions or unsourced material facts",
  },
};

export function ConfidenceBanner({
  confidence,
  isCollapsed,
  onExpand,
}: {
  confidence: Confidence;
  isCollapsed?: boolean;
  onExpand?: () => void;
}) {
  const s = STYLES[confidence];

  return (
    <div
      className={clsx(
        "flex items-center gap-2 px-4 py-3 rounded-lg border text-sm font-medium",
        s.bg,
        s.text,
        isCollapsed && "cursor-pointer hover:opacity-80"
      )}
      onClick={isCollapsed ? onExpand : undefined}
    >
      <span className={s.text}>{s.icon}</span>
      <span className={clsx("flex-1", s.text)}>{s.label}</span>
      {isCollapsed && (
        <span className="text-xs opacity-70">click to show attempt</span>
      )}
    </div>
  );
}
