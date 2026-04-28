"use client";

import { useSearchParams, useRouter } from "next/navigation";
import { useEffect, useState, Suspense } from "react";
import { compare, getParties, getElections, type CompareResult, type Party, type Election } from "@/lib/api";
import ArchiveLink from "@/components/ArchiveLink";
import StatusBadge from "@/components/StatusBadge";

const TOPICS = ["habitação","saúde","educação","economia","emprego","ambiente","segurança","justiça","transportes","tecnologia","administração pública","agricultura","cultura","desporto","outros"];

function ComparePage() {
  const params = useSearchParams();
  const router = useRouter();

  const topic = params.get("topic") ?? "";
  const partiesParam = params.get("parties") ?? "";
  const election = params.get("election") ?? "";

  const [result, setResult] = useState<CompareResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [parties, setParties] = useState<Party[]>([]);
  const [elections, setElections] = useState<Election[]>([]);
  const [selectedParties, setSelectedParties] = useState<string[]>(
    partiesParam ? partiesParam.split(",") : []
  );

  useEffect(() => {
    getParties().then(setParties).catch(() => {});
    getElections().then(setElections).catch(() => {});
  }, []);

  useEffect(() => {
    if (!topic) return;
    setLoading(true);
    const p: Record<string, string> = { topic };
    if (selectedParties.length > 0) p.parties = selectedParties.join(",");
    if (election) p.election = election;
    compare(p)
      .then(setResult)
      .catch(() => setResult(null))
      .finally(() => setLoading(false));
  }, [topic, selectedParties.join(","), election]);

  function updateParam(key: string, value: string) {
    const next = new URLSearchParams(params.toString());
    if (value) next.set(key, value);
    else next.delete(key);
    router.push(`/compare?${next.toString()}`);
  }

  function toggleParty(pid: string) {
    const next = selectedParties.includes(pid)
      ? selectedParties.filter((p) => p !== pid)
      : [...selectedParties, pid];
    setSelectedParties(next);
    updateParam("parties", next.join(","));
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Comparar promessas</h1>

      {/* Controles */}
      <div className="bg-white border border-gray-200 rounded-xl p-5 mb-8 space-y-4">
        <div className="flex flex-wrap gap-4 items-end">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Tema</label>
            <select
              value={topic}
              onChange={(e) => updateParam("topic", e.target.value)}
              className="text-sm border border-gray-300 rounded-md px-3 py-1.5 bg-white focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option value="">Escolher tema…</option>
              {TOPICS.map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Eleição</label>
            <select
              value={election}
              onChange={(e) => updateParam("election", e.target.value)}
              className="text-sm border border-gray-300 rounded-md px-3 py-1.5 bg-white focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option value="">Todas as eleições</option>
              {elections.map((e) => (
                <option key={e.id} value={e.id}>{e.description}</option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-600 mb-2">Partidos</label>
          <div className="flex flex-wrap gap-2">
            {parties.map((p) => (
              <button
                key={p.id}
                onClick={() => toggleParty(p.id)}
                className={`px-3 py-1 rounded-full text-sm font-medium border transition-colors ${
                  selectedParties.includes(p.id)
                    ? "text-white border-transparent"
                    : "bg-white text-gray-600 border-gray-300 hover:border-gray-400"
                }`}
                style={selectedParties.includes(p.id) ? { backgroundColor: p.color, borderColor: p.color } : {}}
              >
                {p.short_name}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Resultados */}
      {!topic ? (
        <p className="text-gray-400 text-sm text-center py-16">Escolhe um tema para comparar.</p>
      ) : loading ? (
        <p className="text-gray-500 text-sm">A carregar…</p>
      ) : !result || result.promise_count === 0 ? (
        <p className="text-gray-500 text-sm">Nenhuma promessa encontrada para este tema.</p>
      ) : (
        <>
          <p className="text-sm text-gray-500 mb-6">
            {result.promise_count} promessas sobre <strong>{topic}</strong>
            {election && ` — ${elections.find((e) => e.id === election)?.description ?? election}`}
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {result.parties.map((party) => (
              <div key={party.id} className="space-y-3">
                <div className="flex items-center gap-2 pb-2 border-b-2" style={{ borderColor: party.color }}>
                  <span className="font-bold text-sm" style={{ color: party.color }}>{party.short_name}</span>
                  <span className="text-xs text-gray-500">{party.promises.length} promessas</span>
                </div>
                {party.promises.map((p) => (
                  <div key={p.id} className="bg-white border border-gray-200 rounded-lg p-3 text-sm space-y-2">
                    <p className="text-gray-900 leading-relaxed">{p.text}</p>
                    <div className="flex items-center justify-between gap-2">
                      <div className="flex items-center gap-1.5">
                        <span className="text-xs text-gray-400">{p.election?.date?.slice(0, 4)}</span>
                        <StatusBadge status={p.status} />
                      </div>
                      <ArchiveLink archivedUrl={p.archived_url} archivedDate={p.archived_date} />
                    </div>
                  </div>
                ))}
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export default function ComparePageWrapper() {
  return (
    <Suspense>
      <ComparePage />
    </Suspense>
  );
}
