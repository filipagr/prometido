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

const TOPIC_LABELS: Record<string, string> = {
  habitação: "Habitação", saúde: "Saúde", educação: "Educação", economia: "Economia",
  emprego: "Emprego", ambiente: "Ambiente", segurança: "Segurança", justiça: "Justiça",
  transportes: "Transportes", tecnologia: "Tecnologia", agricultura: "Agricultura",
  cultura: "Cultura", desporto: "Desporto", "administração pública": "Adm. Pública", outros: "Outros",
};

function LoadingSkeleton({ slowWarning }: { slowWarning: boolean }) {
  return (
    <div className="max-w-3xl mx-auto px-4 py-10">
      <div className="skeleton h-3.5 w-48 rounded mb-10" />
      <div className="space-y-3 mb-8">
        <div className="flex gap-2 mb-5">
          <div className="skeleton h-6 w-10 rounded-md" />
          <div className="skeleton h-6 w-32 rounded-md" />
          <div className="skeleton h-6 w-10 rounded-md" />
        </div>
        <div className="skeleton h-4 w-3/4 rounded" />
        <div className="skeleton h-4 w-5/6 rounded" />
        <div className="skeleton h-4 w-full rounded" />
        <div className="skeleton h-4 w-2/3 rounded" />
      </div>
      <div className="skeleton h-40 rounded-2xl" />
      {slowWarning && (
        <p className="text-center text-[12px] text-neutral-400 mt-8">
          O servidor pode demorar até um minuto a acordar na primeira visita do dia.
        </p>
      )}
    </div>
  );
}

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
      .finally(() => { clearTimeout(slowTimer); setLoading(false); });
    return () => clearTimeout(slowTimer);
  }, [id]);

  if (loading) return <LoadingSkeleton slowWarning={slowWarning} />;

  if (notFound || !promise) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-24 text-center">
        <p className="text-lg font-semibold text-neutral-900 mb-3">Promessa não encontrada</p>
        <Link href="/" className="text-[13px] text-blue-600 hover:text-blue-800 transition-colors">← Voltar ao início</Link>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 fade-in">
      {/* Breadcrumb */}
      <nav className="text-[12px] text-neutral-400 mb-10 flex items-center gap-1.5 flex-wrap">
        <Link href="/" className="hover:text-neutral-700 transition-colors">Início</Link>
        <span className="text-neutral-200">/</span>
        <Link
          href={`/party/${promise.party.id}`}
          className="font-semibold hover:opacity-75 transition-opacity"
          style={{ color: promise.party.color }}
        >
          {promise.party.short_name}
        </Link>
        <span className="text-neutral-200">/</span>
        <span>{promise.election.description}</span>
      </nav>

      {/* Metadata */}
      <div className="flex flex-wrap items-center gap-2 mb-5">
        <span
          className="px-2.5 py-1 rounded-lg text-[13px] font-semibold text-white"
          style={{ backgroundColor: promise.party.color }}
        >
          {promise.party.short_name}
        </span>
        <span className="text-[13px] text-neutral-500">{promise.election.description}</span>
        <SourceBadge tier={promise.tier} />
        <StatusBadge status={promise.status} />
      </div>

      {/* Topic pill */}
      {promise.topic && (
        <div className="mb-6">
          <Link
            href={`/search?topic=${encodeURIComponent(promise.topic)}`}
            className="inline-flex items-center text-[12px] text-neutral-500 bg-neutral-100 hover:bg-neutral-200 px-2.5 py-1 rounded-full font-medium transition-colors duration-150"
          >
            {TOPIC_LABELS[promise.topic] ?? promise.topic}
          </Link>
        </div>
      )}

      {/* Promise blockquote */}
      <blockquote
        className="text-[19px] font-normal text-neutral-900 leading-[1.65] border-l-[2px] pl-5 mb-2 tracking-[-0.01em]"
        style={{ borderColor: promise.party.color }}
      >
        {promise.text}
      </blockquote>

      {promise.context && (
        <p className="text-[13px] text-neutral-400 mt-4 pl-5 italic leading-relaxed">
          {promise.context}
        </p>
      )}

      {/* Divider */}
      <div className="border-t border-neutral-100 my-8" />

      {/* Primary source */}
      <div className="bg-white border border-neutral-200 rounded-2xl p-5 mb-6">
        <div className="flex items-center gap-2 mb-5">
          <p className="text-[11px] font-semibold text-neutral-400 uppercase tracking-widest">Fonte primária</p>
          <SourceBadge tier={promise.tier} />
        </div>

        <div className="space-y-4 mb-5">
          {promise.source.original_url && (
            <div>
              <p className="text-[10px] font-semibold text-neutral-400 uppercase tracking-widest mb-1.5">URL original</p>
              <p className="font-mono text-[11.5px] text-neutral-600 break-all bg-neutral-50 px-3 py-2 rounded-lg border border-neutral-100 leading-relaxed">
                {promise.source.original_url}
              </p>
            </div>
          )}
          <div>
            <p className="text-[10px] font-semibold text-neutral-400 uppercase tracking-widest mb-1.5">Data de arquivo</p>
            <p className="text-[13px] text-neutral-700 font-medium tabular-nums">
              {promise.source.archived_date
                ? `${promise.source.archived_date.slice(6, 8)}/${promise.source.archived_date.slice(4, 6)}/${promise.source.archived_date.slice(0, 4)}`
                : "—"}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 pt-4 border-t border-neutral-100">
          <ArchiveLink archivedUrl={promise.source.archived_url} archivedDate={promise.source.archived_date} />
          <p className="text-[12px] text-neutral-400 leading-relaxed flex-1">
            Abre a página original no Arquivo.pt, com a toolbar do arquivo visível.
          </p>
        </div>
      </div>

      {/* Verification sources */}
      {promise.verification_sources.length > 0 && (
        <div className="mb-6">
          <p className="text-[11px] font-semibold text-neutral-400 uppercase tracking-widest mb-3">
            Fontes de verificação
          </p>
          <div className="space-y-2.5">
            {promise.verification_sources.map((s) => (
              <div key={s.id} className="bg-white border border-neutral-200 rounded-xl p-4">
                <div className="flex items-center justify-between mb-3 gap-2">
                  <span className="text-[12px] font-semibold text-neutral-700 bg-neutral-100 px-2 py-0.5 rounded-md">
                    {USE_TYPE_LABELS[s.use_type] ?? s.use_type}
                  </span>
                  <span className="text-[11px] text-neutral-400 tabular-nums">{s.source_domain} · {s.date}</span>
                </div>
                {s.quote && (
                  <blockquote className="text-[13px] text-neutral-600 italic border-l-2 border-neutral-200 pl-3.5 mb-3 leading-relaxed">
                    &ldquo;{s.quote}&rdquo;
                  </blockquote>
                )}
                <a
                  href={s.archived_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 text-[12px] text-blue-600 hover:text-blue-800 font-medium transition-colors"
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
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 mb-6 text-[13px] text-amber-800 leading-relaxed">
          <strong>Nota:</strong> {promise.status_note}
        </div>
      )}

      {/* Methodology footer */}
      <div className="text-[11px] text-neutral-400 border-t border-neutral-100 pt-5 flex items-center justify-between gap-4 tabular-nums">
        <span>
          Extracção:{" "}
          <span className="text-neutral-500 font-medium">{((promise.confidence?.extraction ?? 0) * 100).toFixed(0)}%</span>
          {" · "}
          Validação:{" "}
          <span className="text-neutral-500 font-medium">{((promise.confidence?.validation ?? 0) * 100).toFixed(0)}%</span>
          {" "}confiança
        </span>
        <Link href="/como-funciona" className="hover:text-neutral-600 underline underline-offset-2 transition-colors not-italic">
          Metodologia →
        </Link>
      </div>
    </div>
  );
}
