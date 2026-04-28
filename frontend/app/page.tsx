import Link from "next/link";
import { getParties, getElections, type Party, type Election } from "@/lib/api";
// Party and Election are used for type annotations below
import SearchBar from "@/components/SearchBar";

const FEATURED_TOPICS = ["habitação", "saúde", "educação", "emprego", "ambiente", "economia"];

export default async function HomePage() {
  const [parties, elections]: [Party[], Election[]] = await Promise.all([
    getParties().catch((): Party[] => []),
    getElections().catch((): Election[] => []),
  ]);

  const totalPromises = parties.reduce((sum: number, p: Party) => sum + p.promise_count, 0);
  const electionsWithData = elections.filter((e: Election) => e.promise_count > 0);

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

      {/* Stats */}
      {totalPromises > 0 && (
        <div className="grid grid-cols-3 gap-4 mb-12 max-w-lg mx-auto text-center">
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <p className="text-2xl font-bold text-gray-900">{totalPromises.toLocaleString("pt")}</p>
            <p className="text-xs text-gray-500 mt-0.5">promessas</p>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <p className="text-2xl font-bold text-gray-900">{parties.filter((p) => p.promise_count > 0).length}</p>
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

      {/* Tópicos */}
      <div>
        <h2 className="font-semibold text-gray-900 mb-4">Pesquisar por tema</h2>
        <div className="flex flex-wrap gap-2">
          {["habitação","saúde","educação","economia","emprego","ambiente","segurança","justiça","transportes","tecnologia"].map((topic) => (
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
