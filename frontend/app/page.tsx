"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { getParties, getElections, warmupBackend, type Party, type Election } from "@/lib/api";
import SearchBar from "@/components/SearchBar";

const ALL_TOPICS = [
  "habitação", "saúde", "educação", "economia", "emprego",
  "ambiente", "segurança", "justiça", "transportes", "tecnologia",
  "administração pública", "agricultura", "cultura", "desporto",
  "imigração", "direitos sociais", "outros",
];

function partyAbbr(name: string): string {
  if (name.length <= 3) return name;
  return name.slice(0, 2);
}

function StatSkeleton() {
  return (
    <div className="text-center">
      <div className="skeleton h-8 w-16 rounded mx-auto mb-1.5" />
      <div className="skeleton h-3 w-20 rounded mx-auto" />
    </div>
  );
}

function PartySkeleton() {
  return (
    <div className="bg-white border border-neutral-200 rounded-xl p-3 flex items-center gap-3">
      <div className="skeleton w-8 h-8 rounded-lg shrink-0" />
      <div className="space-y-1.5 flex-1">
        <div className="skeleton h-3.5 w-10 rounded" />
        <div className="skeleton h-3 w-20 rounded" />
      </div>
    </div>
  );
}

export default function HomePage() {
  const [parties, setParties] = useState<Party[]>([]);
  const [elections, setElections] = useState<Election[]>([]);
  const [loading, setLoading] = useState(true);
  const [slowWarning, setSlowWarning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    warmupBackend();
    const slowTimer = setTimeout(() => setSlowWarning(true), 4000);
    Promise.all([getParties(), getElections()])
      .then(([p, e]) => { setParties(p); setElections(e); setError(null); })
      .catch((err) => setError(err?.message ?? "Não foi possível carregar os dados."))
      .finally(() => { clearTimeout(slowTimer); setLoading(false); });
    return () => clearTimeout(slowTimer);
  }, []);

  const totalPromises = parties.reduce((sum, p) => sum + p.promise_count, 0);
  const electionsWithData = elections.filter((e) => e.promise_count > 0);
  const partiesWithData = parties.filter((p) => p.promise_count > 0);

  return (
    <div>
      {/* Hero */}
      <div className="relative bg-white border-b border-neutral-100 overflow-hidden">
        <div className="absolute inset-0 dot-grid opacity-60 pointer-events-none" />

        <div className="relative max-w-5xl mx-auto px-4 pt-20 pb-16 text-center">
          <div className="inline-flex items-center gap-2 bg-neutral-100 border border-neutral-200 rounded-full px-3 py-1 text-[12px] text-neutral-500 mb-5">
            <span className="w-1.5 h-1.5 rounded-full bg-neutral-400 shrink-0" />
            Em breve — todas as legislativas desde 1975
          </div>

          <h1 className="text-[2.75rem] sm:text-5xl font-semibold text-neutral-950 mb-4 tracking-[-0.03em] leading-[1.15]">
            O que prometeram.
            <br />
            Onde está escrito.
          </h1>

          <p className="text-[15px] text-neutral-600 max-w-lg mx-auto mb-8 leading-relaxed">
            Pesquisa e compara promessas eleitorais de 9 partidos portugueses
            desde 2002, com ligação directa ao programa original.
          </p>

          <div className="max-w-xl mx-auto">
            <SearchBar autoFocus />
          </div>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-4 py-12 space-y-14">

        {/* Error */}
        {!loading && error && (
          <div className="bg-neutral-50 border border-neutral-200 rounded-xl p-5 text-sm text-neutral-700">
            <p className="font-semibold mb-1">Não foi possível carregar os dados.</p>
            <p className="text-neutral-600">
              Tenta recarregar a página. Se o problema persistir,{" "}
              <a href="https://github.com/filipagr/prometido/issues" className="underline underline-offset-2">avisa-nos</a>.
            </p>
          </div>
        )}

        {/* Stats */}
        <div className="grid grid-cols-3 gap-6 max-w-xs mx-auto text-center">
          {loading ? (
            <><StatSkeleton /><StatSkeleton /><StatSkeleton /></>
          ) : totalPromises > 0 ? (
            <>
              <div className="fade-in">
                <p className="text-[1.75rem] font-semibold text-neutral-900 tabular-nums tracking-tight leading-none mb-1.5">{totalPromises.toLocaleString("pt")}</p>
                <p className="text-[11px] text-neutral-600 font-medium uppercase tracking-widest">promessas</p>
              </div>
              <div className="fade-in">
                <p className="text-[1.75rem] font-semibold text-neutral-900 tabular-nums tracking-tight leading-none mb-1.5">{partiesWithData.length}</p>
                <p className="text-[11px] text-neutral-600 font-medium uppercase tracking-widest">partidos</p>
              </div>
              <div className="fade-in">
                <p className="text-[1.75rem] font-semibold text-neutral-900 tabular-nums tracking-tight leading-none mb-1.5">{electionsWithData.length}</p>
                <p className="text-[11px] text-neutral-600 font-medium uppercase tracking-widest">eleições</p>
              </div>
            </>
          ) : null}
        </div>

        {loading && slowWarning && (
          <p className="text-center text-xs text-neutral-500">
            O servidor pode demorar até um minuto a acordar na primeira visita do dia.
          </p>
        )}

        {/* Partidos */}
        <div>
          <h2 className="text-[11px] font-semibold text-neutral-600 uppercase tracking-widest mb-4">Partidos</h2>
          {loading ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-2">
              {Array.from({ length: 9 }).map((_, i) => <PartySkeleton key={i} />)}
            </div>
          ) : parties.length > 0 ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-2 fade-in">
              {parties.map((party) => (
                <Link
                  key={party.id}
                  href={`/party/${party.id}`}
                  className="bg-white border border-neutral-200 rounded-xl p-3 hover:border-neutral-300 hover:shadow-[0_1px_4px_rgba(0,0,0,0.06)] transition-all duration-150 flex items-center gap-2.5 group"
                >
                  <span
                    className="w-8 h-8 rounded-lg shrink-0 flex items-center justify-center text-white font-bold"
                    style={{
                      backgroundColor: party.color,
                      fontSize: party.short_name.length <= 2 ? "12px" : party.short_name.length === 3 ? "10px" : "10px",
                    }}
                  >
                    {partyAbbr(party.short_name)}
                  </span>
                  <div className="min-w-0">
                    <p className="font-semibold text-[13px] text-neutral-900 truncate group-hover:text-neutral-600 transition-colors duration-150">
                      {party.short_name}
                    </p>
                    <p className="text-[11px] text-neutral-500 tabular-nums">{(party.promise_count ?? 0).toLocaleString("pt")}</p>
                  </div>
                </Link>
              ))}
            </div>
          ) : null}
        </div>

        {/* Tópicos */}
        <div>
          <h2 className="text-[11px] font-semibold text-neutral-600 uppercase tracking-widest mb-4">Pesquisar por tema</h2>
          <div className="flex flex-wrap gap-1.5">
            {ALL_TOPICS.map((topic) => (
              <Link
                key={topic}
                href={`/search?topic=${encodeURIComponent(topic)}`}
                className="px-3 py-1.5 text-[13px] font-medium bg-white hover:bg-neutral-50 text-neutral-700 hover:text-neutral-900 border border-neutral-200 hover:border-neutral-400 rounded-full transition-all duration-150"
              >
                {topic}
              </Link>
            ))}
          </div>
        </div>

        {/* Compare feature */}
        <div>
          <h2 className="text-[11px] font-semibold text-neutral-600 uppercase tracking-widest mb-4">Comparar por tema</h2>
          <Link
            href="/compare"
            className="flex items-center justify-between gap-6 bg-white border border-neutral-200 rounded-xl px-5 py-4 hover:border-neutral-400 hover:bg-neutral-50 transition-all duration-150 group"
          >
            <p className="text-[13px] text-neutral-500 leading-relaxed">
              Vê lado a lado o que cada partido prometeu sobre o mesmo tema.
            </p>
            <span className="shrink-0 text-[13px] font-medium text-neutral-700 group-hover:text-neutral-900 transition-colors duration-150">
              Ver comparador →
            </span>
          </Link>
        </div>

      </div>
    </div>
  );
}
