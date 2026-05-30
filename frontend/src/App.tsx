import { useState } from "react";
import { AppShell } from "./components/layout/AppShell";
import { QueueView } from "./components/queue/QueueView";
import { ItemDetailView } from "./components/items/ItemDetailView";
import { DraftReviewView } from "./components/drafts/DraftReviewView";
import { MatterView } from "./views/MatterView";

export type View =
  | { kind: "queue" }
  | { kind: "item"; id: string }
  | { kind: "draft"; itemId: string; draftId: string }
  | { kind: "matter"; id: string };

export default function App() {
  const [view, setView] = useState<View>({ kind: "queue" });

  return (
    <AppShell
      onNavigate={(v) => setView(v)}
      currentView={view}
    >
      {view.kind === "queue" && (
        <QueueView
          onOpenItem={(id) => setView({ kind: "item", id })}
          onOpenMatter={(id) => setView({ kind: "matter", id })}
        />
      )}
      {view.kind === "item" && (
        <ItemDetailView
          itemId={view.id}
          onBack={() => setView({ kind: "queue" })}
          onDraftReady={(itemId, draftId) =>
            setView({ kind: "draft", itemId, draftId })
          }
          onOpenMatter={(id) => setView({ kind: "matter", id })}
        />
      )}
      {view.kind === "draft" && (
        <DraftReviewView
          itemId={view.itemId}
          draftId={view.draftId}
          onBack={() => setView({ kind: "item", id: view.itemId })}
          onApproved={() => setView({ kind: "queue" })}
        />
      )}
      {view.kind === "matter" && (
        <MatterView
          matterId={view.id}
          onBack={() => setView({ kind: "queue" })}
          onOpenItem={(id) => setView({ kind: "item", id })}
        />
      )}
    </AppShell>
  );
}
