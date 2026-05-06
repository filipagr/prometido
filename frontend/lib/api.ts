const API_BASE = "https://prometido-api.onrender.com/api";

// Render free tier dorme após 15min e demora 30-50s a acordar.
// O fetch usa AbortController com timeout de 60s para sobreviver ao cold-start.
const COLD_START_TIMEOUT_MS = 60_000;

async function apiFetch<T>(path: string, params?: Record<string, string>): Promise<T> {
  const url = new URL(`${API_BASE}${path}`);
  if (params) {
    Object.entries(params).forEach(([k, v]) => v && url.searchParams.set(k, v));
  }
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), COLD_START_TIMEOUT_MS);
  try {
    const res = await fetch(url.toString(), { cache: "no-store", signal: ctrl.signal });
    if (!res.ok) throw new Error(`API ${res.status}: ${path}`);
    return res.json();
  } finally {
    clearTimeout(t);
  }
}

// Cache em sessionStorage para listas estáveis (parties, elections).
// Evita re-fetch a cada navegação na mesma sessão.
function readCache<T>(key: string, ttlMs: number): T | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = sessionStorage.getItem(key);
    if (!raw) return null;
    const { t, v } = JSON.parse(raw) as { t: number; v: T };
    if (Date.now() - t > ttlMs) return null;
    return v;
  } catch {
    return null;
  }
}

function writeCache<T>(key: string, value: T) {
  if (typeof window === "undefined") return;
  try {
    sessionStorage.setItem(key, JSON.stringify({ t: Date.now(), v: value }));
  } catch {
    /* quota exceeded — ignora */
  }
}

async function cachedFetch<T>(key: string, ttlMs: number, fetcher: () => Promise<T>): Promise<T> {
  const cached = readCache<T>(key, ttlMs);
  if (cached) return cached;
  const fresh = await fetcher();
  writeCache(key, fresh);
  return fresh;
}

// Acorda o backend Render em background. Não esperar pelo retorno —
// o objectivo é só disparar o cold-start em paralelo com o resto.
export function warmupBackend(): void {
  if (typeof window === "undefined") return;
  fetch(`${API_BASE}/health`, { cache: "no-store" }).catch(() => {});
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
  source_type: "arquivo_pt" | "direct";
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
    source_type: "arquivo_pt" | "direct";
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

// --- API calls ---

const PARTIES_TTL_MS = 5 * 60_000;   // 5 min
const ELECTIONS_TTL_MS = 5 * 60_000; // 5 min

export const getParties = () =>
  cachedFetch("prometido:parties", PARTIES_TTL_MS, () => apiFetch<Party[]>("/parties"));

export const getElections = () =>
  cachedFetch("prometido:elections", ELECTIONS_TTL_MS, () => apiFetch<Election[]>("/elections"));

export const getParty = (id: string) => apiFetch<PartyDetail>(`/party/${id}`);
export const getPromise = (id: string) => apiFetch<PromiseDetail>(`/promise/${id}`);
export const search = (params: Record<string, string>) => apiFetch<SearchResult>("/search", params);
export const compare = (params: Record<string, string>) => apiFetch<CompareResult>("/compare", params);
