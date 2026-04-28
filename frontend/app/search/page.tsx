"use client";

import { useSearchParams, useRouter } from "next/navigation";
import { useEffect, useState, Suspense } from "react";
import { search, getParties, getElections, type PromiseItem, type Party, type Election, type SearchResult } from "@/lib/api";
import PromiseCard from "@/components/PromiseCard";
import SearchBar from "@/components/SearchBar";

const TOPICS = ["habitação","saúde","educação","economia","emprego","ambiente","segurança","justiça","transportes","tecnologia","outros"];

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
      setResults([]);
      setTotal(0);
      return;
    }
    setLoading(true);
    const searchParams: Record<string, string> = {};
    if (q) searchParams.q = q;
    if (partyFilter) searchParams.party = partyFilter;
    if (electionFilter) searchParams.election = electionFilter;
    if (topicFilter) searchParams.topic = topicFilter;

    search(searchParams)
      .then((r: SearchResult) => { setResults(r.results); setTotal(r.total); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [q, partyFilter, electionFilter, topicFilter]);

  function updateFilter(key: string, value: string) {
    const next = new URLSearchParams(params.toString());
    if (value) next.set(key, value);
    else next.delete(key);
    router.push(`/search?${next.toString()}`);
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="mb-6">
        <SearchBar defaultValue={q} />
      </div>

      {/* Filtros */}
      <div className="flex flex-wrap gap-2 mb-6">
        <select
          value={partyFilter}
          onChange={(e) => updateFilter("party", e.target.value)}
          className="text-sm border border-gray-300 rounded-md px-2 py-1.5 bg-white focus:outline-none focus:ring-1 focus:ring-blue-500"
        >
          <option value="">Todos os partidos</option>
          {parties.map((p) => (
            <option key={p.id} value={p.id}>{p.short_name}</option>
          ))}
        </select>

        <select
          value={electionFilter}
          onChange={(e) => updateFilter("election", e.target.value)}
          className="text-sm border border-gray-300 rounded-md px-2 py-1.5 bg-white focus:outline-none focus:ring-1 focus:ring-blue-500"
        >
          <option value="">Todas as eleições</option>
          {elections.map((e) => (
            <option key={e.id} value={e.id}>{e.description}</option>
          ))}
        </select>

        <select
          value={topicFilter}
          onChange={(e) => updateFilter("topic", e.target.value)}
          className="text-sm border border-gray-300 rounded-md px-2 py-1.5 bg-white focus:outline-none focus:ring-1 focus:ring-blue-500"
        >
          <option value="">Todos os temas</option>
          {TOPICS.map((t) => <option key={t} value={t}>{t}</option>)}
        </select>
      </div>

      {/* Resultados */}
      {loading ? (
        <p className="text-gray-500 text-sm">A pesquisar…</p>
      ) : results.length > 0 ? (
        <>
          <p className="text-sm text-gray-500 mb-4">{total} promessas encontradas</p>
          <div className="space-y-3">
            {results.map((p) => <PromiseCard key={p.id} promise={p} />)}
          </div>
        </>
      ) : (q || partyFilter || electionFilter || topicFilter) ? (
        <p className="text-gray-500 text-sm">Nenhuma promessa encontrada.</p>
      ) : (
        <p className="text-gray-400 text-sm">Usa a barra de pesquisa ou os filtros acima.</p>
      )}
    </div>
  );
}

export default function SearchPageWrapper() {
  return (
    <Suspense>
      <SearchPage />
    </Suspense>
  );
}
