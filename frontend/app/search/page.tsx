"use client";

import { useSearchParams, useRouter } from "next/navigation";
import { useEffect, useState, Suspense } from "react";
import { ChevronDown, X } from "lucide-react";
import { search, getParties, getElections, type PromiseItem, type Party, type Election, type SearchResult } from "@/lib/api";
import PromiseCard from "@/components/PromiseCard";
import SearchBar from "@/components/SearchBar";

const TOPICS = ["habitação","saúde","educação","economia","emprego","ambiente","segurança","justiça","transportes","tecnologia","outros"];

function SkeletonCard() {
  return (
    <div className="bg-white border border-neutral-200 rounded-xl overflow-hidden relative">
      <div className="absolute left-0 top-0 bottom-0 w-[2px] bg-neutral-200" />
      <div className="px-4 pt-3.5 pb-3 pl-[18px] space-y-2.5">
        <div className="flex items-center justify-between">
          <div className="flex gap-2">
            <div className="skeleton h-3.5 w-8 rounded" />
            <div className="skeleton h-3.5 w-10 rounded" />
          </div>
          <div className="skeleton h-3 w-16 rounded" />
        </div>
        <div className="space-y-1.5">
          <div className="skeleton h-3.5 w-full rounded" />
          <div className="skeleton h-3.5 w-5/6 rounded" />
          <div className="skeleton h-3.5 w-2/3 rounded" />
        </div>
        <div className="skeleton h-3 w-28 rounded" />
      </div>
    </div>
  );
}

function Select({
  value,
  onChange,
  children,
}: {
  value: string;
  onChange: (v: string) => void;
  children: React.ReactNode;
}) {
  const hasValue = Boolean(value);
  return (
    <div className="relative">
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className={`appearance-none text-[13px] border rounded-lg pl-3 pr-7 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 cursor-pointer transition-all duration-150 font-medium ${
          hasValue
            ? "border-blue-300 text-blue-700 bg-blue-50"
            : "border-neutral-200 text-neutral-600 hover:border-neutral-300"
        }`}
      >
        {children}
      </select>
      <ChevronDown
        size={13}
        className={`absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none ${hasValue ? "text-blue-500" : "text-neutral-400"}`}
      />
    </div>
  );
}

function SearchPage() {
  const params = useSearchParams();
  const router = useRouter();

  const q = params.get("q") ?? "";
  const partyFilter = params.get("party") ?? "";
  const electionFilter = params.get("election") ?? "";
  const topicFilter = params.get("topic") ?? "";

  const [results, setResults] = useState<PromiseItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [parties, setParties] = useState<Party[]>([]);
  const [elections, setElections] = useState<Election[]>([]);

  useEffect(() => {
    getParties().then(setParties).catch(() => {});
    getElections().then(setElections).catch(() => {});
  }, []);

  useEffect(() => {
    if (!q && !partyFilter && !electionFilter && !topicFilter) {
      setResults([]); setTotal(0); return;
    }
    setLoading(true);
    const p: Record<string, string> = {};
    if (q) p.q = q;
    if (partyFilter) p.party = partyFilter;
    if (electionFilter) p.election = electionFilter;
    if (topicFilter) p.topic = topicFilter;
    search(p)
      .then((r: SearchResult) => { setResults(r.results); setTotal(r.total); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [q, partyFilter, electionFilter, topicFilter]);

  function updateFilter(key: string, value: string) {
    const next = new URLSearchParams(params.toString());
    if (value) next.set(key, value); else next.delete(key);
    router.push(`/search?${next.toString()}`);
  }

  function clearFilter(key: string) {
    updateFilter(key, "");
  }

  const activeFilterCount = [partyFilter, electionFilter, topicFilter].filter(Boolean).length;
  const hasSearch = q || partyFilter || electionFilter || topicFilter;
  const partyLabel = parties.find((p) => p.id === partyFilter)?.short_name;
  const electionLabel = elections.find((e) => e.id === electionFilter)?.description;

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="mb-5">
        <SearchBar defaultValue={q} />
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-2 mb-6">
        <Select value={partyFilter} onChange={(v) => updateFilter("party", v)}>
          <option value="">Todos os partidos</option>
          {parties.map((p) => <option key={p.id} value={p.id}>{p.short_name}</option>)}
        </Select>

        <Select value={electionFilter} onChange={(v) => updateFilter("election", v)}>
          <option value="">Todas as eleições</option>
          {elections.map((e) => <option key={e.id} value={e.id}>{e.description}</option>)}
        </Select>

        <Select value={topicFilter} onChange={(v) => updateFilter("topic", v)}>
          <option value="">Todos os temas</option>
          {TOPICS.map((t) => <option key={t} value={t}>{t}</option>)}
        </Select>

        {activeFilterCount > 0 && (
          <button
            onClick={() => { clearFilter("party"); clearFilter("election"); clearFilter("topic"); }}
            className="inline-flex items-center gap-1.5 text-[12px] text-neutral-400 hover:text-neutral-700 transition-colors px-1"
          >
            <X size={12} />
            Limpar {activeFilterCount > 1 ? `${activeFilterCount} filtros` : "filtro"}
          </button>
        )}
      </div>

      {/* Active filter chips */}
      {(partyFilter || electionFilter || topicFilter) && (
        <div className="flex flex-wrap gap-1.5 mb-5">
          {partyFilter && (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-blue-50 border border-blue-200 rounded-full text-[12px] text-blue-700 font-medium">
              {partyLabel ?? partyFilter}
              <button onClick={() => clearFilter("party")} className="text-blue-400 hover:text-blue-700 transition-colors">
                <X size={11} />
              </button>
            </span>
          )}
          {electionFilter && (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-blue-50 border border-blue-200 rounded-full text-[12px] text-blue-700 font-medium">
              {electionLabel ?? electionFilter}
              <button onClick={() => clearFilter("election")} className="text-blue-400 hover:text-blue-700 transition-colors">
                <X size={11} />
              </button>
            </span>
          )}
          {topicFilter && (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-blue-50 border border-blue-200 rounded-full text-[12px] text-blue-700 font-medium">
              {topicFilter}
              <button onClick={() => clearFilter("topic")} className="text-blue-400 hover:text-blue-700 transition-colors">
                <X size={11} />
              </button>
            </span>
          )}
        </div>
      )}

      {/* Results */}
      {loading ? (
        <div className="space-y-2.5">
          {Array.from({ length: 6 }).map((_, i) => <SkeletonCard key={i} />)}
        </div>
      ) : results.length > 0 ? (
        <div className="fade-in">
          <p className="text-[12px] text-neutral-400 font-medium mb-4 tabular-nums">
            {total.toLocaleString("pt")} resultado{total !== 1 ? "s" : ""}
            {total > results.length && (
              <span className="text-neutral-300"> · a mostrar {results.length}</span>
            )}
          </p>
          <div className="space-y-2.5">
            {results.map((p) => <PromiseCard key={p.id} promise={p} />)}
          </div>
        </div>
      ) : hasSearch ? (
        <div className="py-20 text-center">
          <p className="text-neutral-600 font-medium text-[15px] mb-1">Nenhuma promessa encontrada</p>
          <p className="text-[13px] text-neutral-400">Tenta outros termos ou remove alguns filtros.</p>
        </div>
      ) : (
        <div className="py-20 text-center">
          <p className="text-[13px] text-neutral-400">Usa a barra de pesquisa ou os filtros para explorar as promessas.</p>
        </div>
      )}
    </div>
  );
}

export default function SearchPageWrapper() {
  return <Suspense><SearchPage /></Suspense>;
}
