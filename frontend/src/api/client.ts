const BASE = "/api/v1";

async function req<T>(
  method: string,
  path: string,
  body?: unknown
): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`${res.status}: ${err}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export const api = {
  getQueue: (params?: { state?: string; matter_id?: string; min_score?: number; page?: number }) =>
    req("GET", `/queue?${new URLSearchParams(
      Object.entries(params ?? {})
        .filter(([, v]) => v !== undefined)
        .map(([k, v]) => [k, String(v)])
    )}`),

  getItem: (id: string) => req("GET", `/items/${id}`),
  requestDraft: (id: string) => req("POST", `/items/${id}/draft`),
  estimateDraft: (id: string) => req("GET", `/items/${id}/draft/estimate`),
  dismissItem: (id: string, reason: string) =>
    req("POST", `/items/${id}/dismiss`, { reason }),
  snoozeItem: (id: string, snooze_until: string) =>
    req("POST", `/items/${id}/snooze`, { snooze_until }),
  rerankItem: (id: string, new_score: number) =>
    req("POST", `/items/${id}/rerank?new_score=${new_score}`),

  getDraft: (id: string) => req("GET", `/drafts/${id}`),
  patchDraft: (id: string, body: string) =>
    req("PATCH", `/drafts/${id}`, { body }),
  approveDraft: (id: string) => req("POST", `/drafts/${id}/approve`),
  rejectDraft: (id: string) => req("POST", `/drafts/${id}/reject`),

  listMatters: () => req("GET", `/matters`),
  getMatter: (id: string) => req("GET", `/matters/${id}`),
  getMatterCost: (id: string) => req("GET", `/matters/${id}/cost`),

  proposeReviewSlot: (
    itemId: string,
    start: string,
    end: string,
    confirm = false
  ) => req("POST", `/review-slots/${itemId}`, { start, end, confirm }),

  batchDraft: (item_ids: string[], confirmed = false) =>
    req("POST", `/items/draft-batch`, { item_ids, confirmed }),

  getMe: () => req("GET", `/auth/me`),
};
