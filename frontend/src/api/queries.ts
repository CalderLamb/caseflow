import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "./client";
import type {
  QueueResponse,
  CaseItemDetail,
  Draft,
  DraftEstimate,
  MatterDetail,
  Matter,
} from "../types/api";

export const queueKeys = {
  all: ["queue"] as const,
  filtered: (params: object) => ["queue", params] as const,
};

export function useQueue(params?: {
  state?: string;
  matter_id?: string;
  min_score?: number;
  page?: number;
}) {
  return useQuery<QueueResponse>({
    queryKey: queueKeys.filtered(params ?? {}),
    queryFn: () => api.getQueue(params) as Promise<QueueResponse>,
    refetchInterval: 30_000,
  });
}

export function useItem(id: string) {
  return useQuery<CaseItemDetail>({
    queryKey: ["items", id],
    queryFn: () => api.getItem(id) as Promise<CaseItemDetail>,
    enabled: !!id,
  });
}

export function useDraftEstimate(id: string, enabled = false) {
  return useQuery<DraftEstimate>({
    queryKey: ["items", id, "estimate"],
    queryFn: () => api.estimateDraft(id) as Promise<DraftEstimate>,
    enabled,
    staleTime: 60_000,
  });
}

export function useDraft(id: string | null) {
  return useQuery<Draft>({
    queryKey: ["drafts", id],
    queryFn: () => api.getDraft(id!) as Promise<Draft>,
    enabled: !!id,
  });
}

export function useMatters() {
  return useQuery<Matter[]>({
    queryKey: ["matters"],
    queryFn: () => api.listMatters() as Promise<Matter[]>,
    staleTime: 120_000,
  });
}

export function useMatter(id: string) {
  return useQuery<MatterDetail>({
    queryKey: ["matters", id],
    queryFn: () => api.getMatter(id) as Promise<MatterDetail>,
    enabled: !!id,
  });
}

export function useRequestDraft() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (itemId: string) => api.requestDraft(itemId) as Promise<Draft>,
    onSuccess: (_, itemId) => {
      qc.invalidateQueries({ queryKey: ["items", itemId] });
      qc.invalidateQueries({ queryKey: queueKeys.all });
    },
  });
}

export function useApproveDraft() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (draftId: string) => api.approveDraft(draftId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queueKeys.all });
      qc.invalidateQueries({ queryKey: ["drafts"] });
    },
  });
}

export function usePatchDraft() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, body }: { id: string; body: string }) =>
      api.patchDraft(id, body) as Promise<Draft>,
    onSuccess: (_, { id }) => {
      qc.invalidateQueries({ queryKey: ["drafts", id] });
    },
  });
}

export function useDismissItem() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, reason }: { id: string; reason: string }) =>
      api.dismissItem(id, reason),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queueKeys.all });
    },
  });
}

export function useSnoozeItem() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, until }: { id: string; until: string }) =>
      api.snoozeItem(id, until),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queueKeys.all });
    },
  });
}

export function useConfirmReviewSlot() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      itemId,
      start,
      end,
      confirm,
    }: {
      itemId: string;
      start: string;
      end: string;
      confirm: boolean;
    }) => api.proposeReviewSlot(itemId, start, end, confirm),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queueKeys.all });
    },
  });
}
