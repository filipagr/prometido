const API_BASE = "https://prometido-api.onrender.com/api";

async function apiFetch<T>(path: string, params?: Record<string, string>): Promise<T> {
  const url = new URL(`${API_BASE}${path}`);
  if (params) {
    Object.entries(params).forEach(([k, v]) => v && url.searchParams.set(k, v));
  }
  const res = await fetch(url.toString(), { cache: "no-store" });
  if (!res.ok) throw new Error(`API ${res.status}: ${path}`);
  return res.json();
}

// --- Types ---

export type Party = {
  id: string;
  name: string;
  short_name: string;
  color: string;
  founded: string;
  promise_count: number;
  elections_covered: number;
  notes?: string;
};

export type Election = {
  id: string;
  type: string;
  date: string;
  description: string;
  promise_count: number;
  parties_covered: number;
};

export type PromiseItem = {
  id: string;
  text: string;
  topic: string;
  tier: number;
  status: string;
  confidence?: number;
  party: { id: string; name: string; short_name: string; color: string };
  election: { id: string; date: string; description: string };
  archived_url: string;
  archived_date: string;
};

export type PromiseDetail = PromiseItem & {
  context?: string;
  status_note?: string;
  confidence: { extraction: number; validation: number };
  source: {
    archived_url: string;
    original_url: string;
    archived_date: string;
    archived_datetime: string;
  };
  verification_sources: {
    id: string;
    archived_url: string;
    source_domain: string;
    date: string;
    use_type: string;
    quote?: string;
    added_by: string;
  }[];
};

export type SearchResult = {
  total: number;
  offset: number;
  limit: number;
  results: PromiseItem[];
};

export type CompareResult = {
  topic: string;
  election_filter?: string;
  promise_count: number;
  parties: {
    id: string;
    name: string;
    short_name: string;
    color: string;
    promises: PromiseItem[];
  }[];
};

// --- API calls ---

export const getParties = () => apiFetch<Party[]>("/parties");
export type PartyElection = {
  id: string;
  date: string;
  description: string;
  promise_count: number;
  statuses: Record<string, number>;
};

export type PartyDetail = Party & {
  elections: PartyElection[];
  topics: { topic: string; count: number }[];
};

export const getParty = (id: string) => apiFetch<PartyDetail>(`/party/${id}`);
export const getElections = () => apiFetch<Election[]>("/elections");
export const getPromise = (id: string) => apiFetch<PromiseDetail>(`/promise/${id}`);
export const search = (params: Record<string, string>) => apiFetch<SearchResult>("/search", params);
export const compare = (params: Record<string, string>) => apiFetch<CompareResult>("/compare", params);
