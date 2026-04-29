"use client";

import { use, useEffect, useState } from "react";
import Link from "next/link";
import {
  getParty, search, warmupBackend,
  type PartyDetail, type PartyElection, type PromiseItem, type SearchResult,
} from "@/lib/api";
import PromiseCard from "@/components/PromiseCard";

export default function PartyPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);

  const [party, setParty] = useState<PartyDetail | null>(null);
  const [promises, setPromises] = useState<SearchResult>({ total: 0, offset: 0, limit: 20, results: [] });
  const [loading, setLoading] = useState(true);
  const [slowWarning, setSlowWarning] = useState(false);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    warmupBackend();
    const slowTimer = setTimeout(() => setSlowWarning(true), 4000);

    Promise.all([
      getParty(id),
      search({ party: id, limit: "20" }).catch(() => ({ total: 0, offset: 0, limit: 20, results: [] as PromiseItem[] })),
    ])
      .then(([p, r]) => {
        setParty(p);
        setPromises(r);
      })
      .catch(() => setNotFound(true))
      .finally(() => {
        clearTimeout(slowTimer);
        setLoading(false);
      });

    return () => clearTimeout(slowTimer);
  }, [id]);

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-16 text-center">
        <p className="text-sm text-gray-500">A carregar partido…</p>
        {slowWarning && (
          <p className="text-xs text-gray-400 mt-2 max-w-md mx-auto">
            O servidor pode demorar até um minuto a acordar na primeira visita do dia.
          </p>
        )}
      </div>
    );
  }

  if (notFound || !party) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-16 text-center">
        <h1 className="text-xl font-semibold text-gray-900 mb-2">Partido não encontrado</h1>
        <p className="text-sm text-gray-500 mb-6">
          O identificador <code className="font-mono bg-gray-100 px-1.5 py-0.5 rounded">{id}</code> não existe na base de dados.
        </p>
        <Link href="/" className="text-sm text-blue-600 hover:underline">← Voltar ao início</Link>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      {/* Cabeçalho */}
      <div className="flex items-center gap-4 mb-8">
        <div className="w-4 h-12 rounded" style={{ backgroundColor: party.color }} />
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{party.name}</h1>
          <p className="text-gray-500 text-sm">
            {party.promise_count} promessas · {party.elections_covered} eleições cobertas
            {party.founded && ` · fundado em ${party.founded.slice(0, 4)}`}
          </p>
        </div>
      </div>

      {/* Nota CDS — participação em coligações */}
      {id === "CDS" && (
        <div className="mb-8 bg-amber-50 border border-amber-200 rounded-lg px-4 py-3 text-sm text-amber-800">
          <p>
            Em <strong>2015</strong> (Portugal à Frente), <strong>2022</strong>, <strong>2024</strong> e <strong>2025</strong> (Aliança Democrática)
            o CDS concorreu em coligação com o PSD. Os programas e promessas dessas eleições estão registados
            em{" "}
            <Link href="/party/PSD" className="underline hover:text-amber-900">PSD / AD</Link>.
          </p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Eleições */}
        <div className="md:col-span-1 space-y-4">
          <h2 className="font-semibold text-gray-900">Por eleição</h2>
          {party.elections.length === 0 ? (
            <p className="text-sm text-gray-400">Sem dados ainda.</p>
          ) : (
            party.elections.map((e: PartyElection) => (
              <Link
                key={e.id}
                href={`/search?party=${id}&election=${e.id}`}
                className="block bg-white border border-gray-200 rounded-lg p-3 hover:border-gray-300 transition-all"
              >
                <p className="font-medium text-sm text-gray-900">{e.description}</p>
                <p className="text-xs text-gray-500 mt-0.5">{e.promise_count} promessas</p>
                {(e.statuses.implemented + e.statuses.not_implemented + e.statuses.partial) > 0 && (
                  <div className="flex gap-2 mt-1.5 flex-wrap">
                    {e.statuses.implemented > 0 && (
                      <span className="text-xs text-green-700 bg-green-50 px-1.5 py-0.5 rounded">
                        ✓ {e.statuses.implemented} cumpridas
                      </span>
                    )}
                    {e.statuses.not_implemented > 0 && (
                      <span className="text-xs text-red-700 bg-red-50 px-1.5 py-0.5 rounded">
                        ✗ {e.statuses.not_implemented} não cumpridas
                      </span>
                    )}
                    {e.statuses.partial > 0 && (
                      <span className="text-xs text-orange-700 bg-orange-50 px-1.5 py-0.5 rounded">
                        ~ {e.statuses.partial} parciais
                      </span>
                    )}
                  </div>
                )}
              </Link>
            ))
          )}

          {/* Tópicos */}
          {party.topics.length > 0 && (
            <>
              <h2 className="font-semibold text-gray-900 pt-4">Por tema</h2>
              <div className="flex flex-wrap gap-1.5">
                {party.topics.map((t) => (
                  <Link
                    key={t.topic}
                    href={`/search?party=${id}&topic=${encodeURIComponent(t.topic)}`}
                    className="px-2 py-1 bg-gray-100 hover:bg-gray-200 rounded text-xs text-gray-700 transition-colors"
                  >
                    {t.topic} <span className="text-gray-400">({t.count})</span>
                  </Link>
                ))}
              </div>
            </>
          )}
        </div>

        {/* Promessas recentes */}
        <div className="md:col-span-2 space-y-3">
          <div className="flex items-center justify-between mb-1">
            <h2 className="font-semibold text-gray-900">Promessas recentes</h2>
            <Link href={`/search?party=${id}`} className="text-sm text-blue-600 hover:underline">
              Ver todas ({promises.total})
            </Link>
          </div>
          {promises.results.length === 0 ? (
            <p className="text-sm text-gray-400">Sem promessas extraídas ainda.</p>
          ) : (
            promises.results.map((p: PromiseItem) => (
              <PromiseCard key={p.id} promise={p} showParty={false} />
            ))
          )}
        </div>
      </div>
    </div>
  );
}
