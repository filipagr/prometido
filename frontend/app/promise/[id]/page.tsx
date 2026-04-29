"use client";

import { use, useEffect, useState } from "react";
import Link from "next/link";
import { ExternalLink } from "lucide-react";
import { getPromise, warmupBackend, type PromiseDetail } from "@/lib/api";
import SourceBadge from "@/components/SourceBadge";
import StatusBadge from "@/components/StatusBadge";
import ArchiveLink from "@/components/ArchiveLink";

const USE_TYPE_LABELS: Record<string, string> = {
  corroboration: "Corroboração",
  fulfillment: "Evidência de cumprimento",
  breach: "Evidência de não cumprimento",
};

export default function PromisePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);

  const [promise, setPromise] = useState<PromiseDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [slowWarning, setSlowWarning] = useState(false);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    warmupBackend();
    const slowTimer = setTimeout(() => setSlowWarning(true), 4000);

    getPromise(id)
      .then(setPromise)
      .catch(() => setNotFound(true))
      .finally(() => {
        clearTimeout(slowTimer);
        setLoading(false);
      });

    return () => clearTimeout(slowTimer);
  }, [id]);

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16 text-center">
        <p className="text-sm text-gray-500">A carregar promessa…</p>
        {slowWarning && (
          <p className="text-xs text-gray-400 mt-2 max-w-md mx-auto">
            O servidor pode demorar até um minuto a acordar na primeira visita do dia.
          </p>
        )}
      </div>
    );
  }

  if (notFound || !promise) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16 text-center">
        <h1 className="text-xl font-semibold text-gray-900 mb-2">Promessa não encontrada</h1>
        <Link href="/" className="text-sm text-blue-600 hover:underline">← Voltar ao início</Link>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      {/* Breadcrumb */}
      <nav className="text-xs text-gray-500 mb-6 flex items-center gap-1.5">
        <Link href="/" className="hover:text-gray-700">Início</Link>
        <span>/</span>
        <Link href={`/party/${promise.party.id}`} className="hover:text-gray-700" style={{ color: promise.party.color }}>
          {promise.party.short_name}
        </Link>
        <span>/</span>
        <span>{promise.election.description}</span>
      </nav>

      {/* Header */}
      <div className="mb-6">
        <div className="flex flex-wrap items-center gap-2 mb-3">
          <span
            className="px-2.5 py-1 rounded text-sm font-semibold text-white"
            style={{ backgroundColor: promise.party.color }}
          >
            {promise.party.short_name}
          </span>
          <span className="text-sm text-gray-500">{promise.election.description}</span>
          <SourceBadge tier={promise.tier} />
          <StatusBadge status={promise.status} />
        </div>

        {promise.topic && (
          <span className="inline-block text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded mb-3">
            {promise.topic}
          </span>
        )}

        <blockquote className="text-lg text-gray-900 leading-relaxed border-l-4 pl-4" style={{ borderColor: promise.party.color }}>
          {promise.text}
        </blockquote>

        {promise.context && (
          <p className="text-sm text-gray-500 mt-3 italic">
            Contexto: {promise.context}
          </p>
        )}
      </div>

      {/* Fonte primária */}
      <div className="bg-stone-50 border border-stone-200 rounded-xl p-5 mb-6">
        <h2 className="font-semibold text-stone-800 mb-3 flex items-center gap-2">
          <span>Fonte primária</span>
          <SourceBadge tier={promise.tier} />
        </h2>
        <div className="space-y-2 text-sm text-stone-700">
          {promise.source.original_url && (
            <p>
              <span className="text-stone-500">URL original:</span>{" "}
              <span className="font-mono text-xs break-all">{promise.source.original_url}</span>
            </p>
          )}
          <p>
            <span className="text-stone-500">Data de arquivo:</span>{" "}
            {promise.source.archived_date
              ? `${promise.source.archived_date.slice(6, 8)}/${promise.source.archived_date.slice(4, 6)}/${promise.source.archived_date.slice(0, 4)}`
              : "—"}
          </p>
        </div>
        <div className="mt-4">
          <ArchiveLink
            archivedUrl={promise.source.archived_url}
            archivedDate={promise.source.archived_date}
            className="text-sm"
          />
          <p className="text-xs text-stone-500 mt-2">
            O link abre a página original congelada no Arquivo.pt — com a toolbar do arquivo visível.
          </p>
        </div>
      </div>

      {/* Fontes de verificação */}
      {promise.verification_sources.length > 0 && (
        <div className="mb-6">
          <h2 className="font-semibold text-gray-900 mb-3">Fontes de verificação</h2>
          <div className="space-y-3">
            {promise.verification_sources.map((s) => (
              <div key={s.id} className="bg-white border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-medium text-gray-600">
                    {USE_TYPE_LABELS[s.use_type] ?? s.use_type}
                  </span>
                  <span className="text-xs text-gray-400">{s.source_domain} · {s.date}</span>
                </div>
                {s.quote && (
                  <blockquote className="text-sm text-gray-700 italic border-l-2 border-gray-200 pl-3 mb-2">
                    &ldquo;{s.quote}&rdquo;
                  </blockquote>
                )}
                <a
                  href={s.archived_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-xs text-blue-600 hover:underline"
                >
                  <ExternalLink size={11} />
                  Ver artigo no Arquivo.pt
                </a>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Status note */}
      {promise.status_note && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-6 text-sm text-amber-800">
          <strong>Nota:</strong> {promise.status_note}
        </div>
      )}

      {/* Metodologia */}
      <div className="text-xs text-gray-400 border-t pt-4 flex items-center justify-between">
        <span>
          Extracção: {((promise.confidence?.extraction ?? 0) * 100).toFixed(0)}% confiança ·
          Validação: {((promise.confidence?.validation ?? 0) * 100).toFixed(0)}%
        </span>
        <Link href="/como-funciona" className="hover:text-gray-600 underline">
          Como funciona a metodologia?
        </Link>
      </div>
    </div>
  );
}
