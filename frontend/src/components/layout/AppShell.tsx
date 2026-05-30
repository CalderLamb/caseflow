import { Inbox, Briefcase, Calendar, Settings } from "lucide-react";
import type { View } from "../../App";
import { useMatters } from "../../api/queries";
import { clsx } from "clsx";

interface Props {
  children: React.ReactNode;
  onNavigate: (v: View) => void;
  currentView: View;
}

export function AppShell({ children, onNavigate, currentView }: Props) {
  const { data: matters } = useMatters();
  const totalOpen = matters?.reduce((s, m) => s + m.open_item_count, 0) ?? 0;

  return (
    <div className="flex h-screen overflow-hidden bg-neutral-50">
      {/* Nav rail */}
      <nav className="w-14 flex flex-col items-center py-4 gap-1 bg-white border-r border-neutral-200/60 shrink-0">
        <div className="mb-4 text-neutral-800 font-medium text-xs tracking-tight select-none px-1 text-center leading-tight">
          CF
        </div>

        <NavItem
          icon={<Inbox size={17} />}
          label="queue"
          active={currentView.kind === "queue"}
          badge={totalOpen > 0 ? totalOpen : undefined}
          onClick={() => onNavigate({ kind: "queue" })}
        />
        <NavItem
          icon={<Briefcase size={17} />}
          label="matters"
          active={currentView.kind === "matter"}
          onClick={() => onNavigate({ kind: "queue" })}
        />
        <NavItem
          icon={<Calendar size={17} />}
          label="calendar"
          active={false}
          onClick={() => {}}
        />

        <div className="flex-1" />
        <NavItem
          icon={<Settings size={17} />}
          label="settings"
          active={false}
          onClick={() => {}}
        />
      </nav>

      {/* Main content */}
      <main className="flex-1 overflow-auto">{children}</main>
    </div>
  );
}

function NavItem({
  icon,
  label,
  active,
  badge,
  onClick,
}: {
  icon: React.ReactNode;
  label: string;
  active: boolean;
  badge?: number;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      title={label}
      className={clsx(
        "relative w-9 h-9 rounded-md flex items-center justify-center transition-colors",
        active
          ? "bg-neutral-100 text-neutral-800"
          : "text-neutral-400 hover:text-neutral-600 hover:bg-neutral-50"
      )}
    >
      {icon}
      {badge !== undefined && (
        <span className="absolute -top-0.5 -right-0.5 min-w-[14px] h-[14px] flex items-center justify-center bg-critical text-white text-[9px] font-medium rounded-full px-0.5">
          {badge > 99 ? "99+" : badge}
        </span>
      )}
    </button>
  );
}
