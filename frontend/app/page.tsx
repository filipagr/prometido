"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { getParties, getElections, warmupBackend, type Party, type Election } from "@/lib/api";
import SearchBar from "@/components/SearchBar";

const FEATURED_TOPICS = ["habitação", "saúde", "educação", "emprego", "ambiente", "economia"];
const SEARCH_TOPICS = [
  "habitação", "saúde", "educação", "economia", "emprego",
  "ambiente", "segurança", "justiça", "transportes", "tecnologia",
];

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
      .then(([p, e]) => {
        setParties(p);
        setElections(e);
        setError(null);
      })
      .catch((err) => {
        setError(err?.message ?? "Não foi possível carregar os dados.");
      })
      .finally(() => {
        clearTimeout(slowTimer);
        setLoading(false);
      });

    return () => clearTimeout(slowTimer);
  }, []);

  const totalPromises = parties.reduce((sum, p) => sum + p.promise_count, 0);
  const electionsWithData = elections.filter((e) => e.promise_count > 0);
  const partiesWithData = parties.filter((p) => p.promise_count > 0);

  return (
    <div className="max-w-5xl mx-auto px-4 py-12">
      {/* Hero */}
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-3 tracking-tight">
          O que prometeram.
          <br />
          <span className="text-blue-600">Onde está a prova.</span>
        </h1>
        <p className="text-lg text-gray-600 max-w-xl mx-auto mb-8">
          Promessas eleitorais de partidos políticos portugueses desde 2002,
          com fonte primária arquivada no{" "}
          <a href="https://arquivo.pt" target="_blank" rel="noopener noreferrer" className="underline hover:text-blue-700">
            Arquivo.pt
          </a>
          .
        </p>
        <div className="max-w-xl mx-auto">
          <SearchBar autoFocus />
        </div>
      </div>

      {/* Loading state */}
      {loading && (
        <div className="text-center py-8 mb-8">
          <p className="text-sm text-gray-500">A carregar dados…</p>
          {slowWarning && (
            <p className="text-xs text-gray-400 mt-2 max-w-md mx-auto">
              O servidor pode demorar até um minuto a acordar na primeira visita do dia.
            </p>
          )}
        </div>
      )}

      {/* Erro */}
      {!loading && error && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-5 mb-8 text-sm text-amber-800">
          <p className="font-medium mb-1">Não foi possível carregar os dados.</p>
          <p className="text-amber-700">
            Tenta recarregar a página dentro de alguns segundos. Se o problema persistir,{" "}
            <a href="https://github.com/filipagr/prometido/issues" className="underline">avisa-nos</a>.
          </p>
        </div>
      )}

      {/* Stats */}
      {!loading && totalPromises > 0 && (
        <div className="grid grid-cols-3 gap-4 mb-12 max-w-lg mx-auto text-center">
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <p className="text-2xl font-bold text-gray-900">{totalPromises.toLocaleString("pt")}</p>
            <p className="text-xs text-gray-500 mt-0.5">promessas</p>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <p className="text-2xl font-bold text-gray-900">{partiesWithData.length}</p>
            <p className="text-xs text-gray-500 mt-0.5">partidos</p>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <p className="text-2xl font-bold text-gray-900">{electionsWithData.length}</p>
            <p className="text-xs text-gray-500 mt-0.5">eleições</p>
          </div>
        </div>
      )}

      {/* Feature: Comparar */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-6 mb-12">
        <h2 className="font-semibold text-blue-900 mb-1">Comparar partidos por tema</h2>
        <p className="text-sm text-blue-700 mb-4">
          O que prometeram PS, PSD e BE sobre habitação entre 2015 e 2022?
        </p>
        <div className="flex flex-wrap gap-2">
          {FEATURED_TOPICS.map((topic) => (
            <Link
              key={topic}
              href={`/compare?topic=${encodeURIComponent(topic)}`}
              className="px-3 py-1.5 bg-white hover:bg-blue-600 hover:text-white text-blue-700 border border-blue-300 rounded-full text-sm font-medium transition-colors"
            >
              {topic}
            </Link>
          ))}
        </div>
      </div>

      {/* Partidos */}
      {!loading && parties.length > 0 && (
        <div className="mb-12">
          <h2 className="font-semibold text-gray-900 mb-4">Partidos</h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
            {parties.map((party) => (
              <Link
                key={party.id}
                href={`/party/${party.id}`}
                className="bg-white border border-gray-200 rounded-lg p-3 hover:border-gray-300 hover:shadow-sm transition-all flex items-center gap-2.5"
              >
                <span className="w-3 h-3 rounded-full shrink-0" style={{ backgroundColor: party.color }} />
                <div className="min-w-0">
                  <p className="font-medium text-sm text-gray-900 truncate">{party.short_name}</p>
                  <p className="text-xs text-gray-500">{party.promise_count} promessas</p>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Tópicos */}
      <div>
        <h2 className="font-semibold text-gray-900 mb-4">Pesquisar por tema</h2>
        <div className="flex flex-wrap gap-2">
          {SEARCH_TOPICS.map((topic) => (
            <Link
              key={topic}
              href={`/search?topic=${encodeURIComponent(topic)}`}
              className="px-3 py-1.5 bg-white hover:bg-gray-100 text-gray-700 border border-gray-200 rounded-full text-sm transition-colors"
            >
              {topic}
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
