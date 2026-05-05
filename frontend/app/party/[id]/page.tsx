"use client";

import { use, useEffect, useState } from "react";
import Link from "next/link";
import {
  getParty, search, warmupBackend,
  type PartyDetail, type PartyElection, type PromiseItem, type SearchResult,
} from "@/lib/api";
import PromiseCard from "@/components/PromiseCard";

function partyAbbr(name: string): string {
  if (name.length <= 3) return name;
  return name.slice(0, 2);
}

function LoadingSkeleton({ slowWarning }: { slowWarning: boolean }) {
  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="flex items-center gap-4 mb-10">
        <div className="skeleton w-1 h-12 rounded-full" />
        <div className="space-y-2">
          <div className="skeleton h-6 w-36 rounded" />
          <div className="skeleton h-4 w-52 rounded" />
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="space-y-2.5">
          {Array.from({ length: 5 }).map((_, i) => <div key={i} className="skeleton h-14 rounded-xl" />)}
        </div>
        <div className="md:col-span-2 space-y-2.5">
          {Array.from({ length: 5 }).map((_, i) => <div key={i} className="skeleton h-24 rounded-xl" />)}
        </div>
      </div>
      {slowWarning && (
        <p className="text-center text-[12px] text-neutral-400 mt-8">
          O servidor pode demorar até um minuto a acordar na primeira visita do dia.
        </p>
      )}
    </div>
  );
}

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
      .then(([p, r]) => { setParty(p); setPromises(r); })
      .catch(() => setNotFound(true))
      .finally(() => { clearTimeout(slowTimer); setLoading(false); });
    return () => clearTimeout(slowTimer);
  }, [id]);

  if (loading) return <LoadingSkeleton slowWarning={slowWarning} />;

  if (notFound || !party) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-24 text-center">
        <p className="text-lg font-semibold text-neutral-900 mb-2">Partido não encontrado</p>
        <p className="text-[13px] text-neutral-500 mb-6">
          O identificador{" "}
          <code className="font-mono bg-neutral-100 px-1.5 py-0.5 rounded text-neutral-700">{id}</code>{" "}
          não existe na base de dados.
        </p>
        <Link href="/" className="text-[13px] text-blue-600 hover:text-blue-800 transition-colors">← Voltar ao início</Link>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 fade-in">
      {/* Header */}
      <div className="flex items-center gap-4 mb-10">
        <div className="w-1 h-12 rounded-full" style={{ backgroundColor: party.color }} />
        <div className="flex items-center gap-3">
          <span
            className="w-10 h-10 rounded-xl shrink-0 flex items-center justify-center text-white font-bold"
            style={{
              backgroundColor: party.color,
              fontSize: party.short_name.length <= 2 ? "14px" : party.short_name.length === 3 ? "11px" : "10px",
            }}
          >
            {partyAbbr(party.short_name)}
          </span>
          <div>
            <h1 className="text-[22px] font-semibold text-neutral-950 tracking-[-0.02em]">{party.name}</h1>
            <p className="text-[13px] text-neutral-400">
              <span className="tabular-nums font-medium text-neutral-500">{(party.promise_count ?? 0).toLocaleString("pt")}</span> promessas
              {" · "}
              <span className="tabular-nums font-medium text-neutral-500">{party.elections_covered}</span> eleições
              {party.founded && (
                <> · fundado em <span className="tabular-nums font-medium text-neutral-500">{party.founded.slice(0, 4)}</span></>
              )}
            </p>
          </div>
        </div>
      </div>

      {/* CDS note */}
      {id === "CDS" && (
        <div className="mb-8 bg-amber-50 border border-amber-200 rounded-xl px-4 py-3.5 text-[13px] text-amber-800">
          Em <strong>2015</strong> (Portugal à Frente), <strong>2022</strong>, <strong>2024</strong> e{" "}
          <strong>2025</strong> (Aliança Democrática) o CDS concorreu em coligação com o PSD.
          Programas e promessas dessas eleições estão em{" "}
          <Link href="/party/PSD" className="underline underline-offset-2 hover:text-amber-900">PSD / AD</Link>.
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Sidebar */}
        <div className="md:col-span-1 space-y-2">
          <p className="text-[11px] font-semibold text-neutral-400 uppercase tracking-widest mb-3">Por eleição</p>
          {party.elections.length === 0 ? (
            <p className="text-[13px] text-neutral-400">Sem dados ainda.</p>
          ) : (
            party.elections.map((e: PartyElection) => (
              <Link
                key={e.id}
                href={`/search?party=${id}&election=${e.id}`}
                className="block bg-white border border-neutral-200 rounded-xl p-3.5 hover:border-neutral-300 hover:shadow-[0_1px_4px_rgba(0,0,0,0.06)] transition-all duration-150 group"
              >
                <div className="flex items-center justify-between gap-2">
                  <p className="font-medium text-[13px] text-neutral-800 group-hover:text-blue-700 transition-colors duration-150">
                    {e.description}
                  </p>
                  <span className="text-[11px] text-neutral-400 tabular-nums shrink-0">{e.promise_count}</span>
                </div>
                {(e.statuses.implemented + e.statuses.not_implemented + e.statuses.partial) > 0 && (
                  <div className="flex gap-1.5 mt-2 flex-wrap">
                    {e.statuses.implemented > 0 && (
                      <span className="text-[11px] text-green-700 bg-green-50 border border-green-200 px-1.5 py-0.5 rounded-md font-medium">✓ {e.statuses.implemented}</span>
                    )}
                    {e.statuses.not_implemented > 0 && (
                      <span className="text-[11px] text-red-600 bg-red-50 border border-red-200 px-1.5 py-0.5 rounded-md font-medium">✗ {e.statuses.not_implemented}</span>
                    )}
                    {e.statuses.partial > 0 && (
                      <span className="text-[11px] text-orange-700 bg-orange-50 border border-orange-200 px-1.5 py-0.5 rounded-md font-medium">~ {e.statuses.partial}</span>
                    )}
                  </div>
                )}
              </Link>
            ))
          )}

          {party.topics.length > 0 && (
            <>
              <p className="text-[11px] font-semibold text-neutral-400 uppercase tracking-widest pt-5 pb-1">Por tema</p>
              <div className="flex flex-wrap gap-1.5">
                {party.topics.map((t) => (
                  <Link
                    key={t.topic}
                    href={`/search?party=${id}&topic=${encodeURIComponent(t.topic)}`}
                    className="px-2.5 py-1 bg-white hover:bg-neutral-50 border border-neutral-200 hover:border-neutral-300 rounded-full text-[12px] text-neutral-600 font-medium transition-all duration-150"
                  >
                    {t.topic}
                    <span className="text-neutral-400 ml-1 tabular-nums">({t.count})</span>
                  </Link>
                ))}
              </div>
            </>
          )}
        </div>

        {/* Promises */}
        <div className="md:col-span-2 space-y-2.5">
          <div className="flex items-center justify-between mb-2">
            <p className="text-[11px] font-semibold text-neutral-400 uppercase tracking-widest">Promessas recentes</p>
            <Link
              href={`/search?party=${id}`}
              className="text-[12px] font-medium text-neutral-400 hover:text-neutral-800 transition-colors"
            >
              Ver todas ({promises.total.toLocaleString("pt")}) →
            </Link>
          </div>
          {promises.results.length === 0 ? (
            <p className="text-[13px] text-neutral-400 py-4">Sem promessas extraídas ainda.</p>
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
