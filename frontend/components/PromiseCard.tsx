import Link from "next/link";
import type { PromiseItem } from "@/lib/api";
import SourceBadge from "./SourceBadge";
import StatusBadge from "./StatusBadge";
import ArchiveLink from "./ArchiveLink";

type Props = {
  promise: PromiseItem;
  showParty?: boolean;
  showElection?: boolean;
};

const TOPIC_LABELS: Record<string, string> = {
  habitação: "Habitação",
  saúde: "Saúde",
  educação: "Educação",
  economia: "Economia",
  emprego: "Emprego",
  ambiente: "Ambiente",
  segurança: "Segurança",
  justiça: "Justiça",
  transportes: "Transportes",
  tecnologia: "Tecnologia",
  agricultura: "Agricultura",
  cultura: "Cultura",
  desporto: "Desporto",
  "administração pública": "Adm. Pública",
  outros: "Outros",
};

export default function PromiseCard({ promise, showParty = true, showElection = true }: Props) {
  return (
    <article className="bg-white border border-gray-200 rounded-lg p-4 hover:border-gray-300 hover:shadow-sm transition-all">
      <div className="flex items-start justify-between gap-3 mb-2">
        <div className="flex flex-wrap items-center gap-1.5">
          {showParty && (
            <span
              className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold text-white"
              style={{ backgroundColor: promise.party.color }}
            >
              {promise.party.short_name}
            </span>
          )}
          {showElection && (
            <span className="text-xs text-gray-500">{promise.election.date?.slice(0, 4)}</span>
          )}
          {promise.topic && (
            <span className="text-xs text-gray-500 bg-gray-100 px-1.5 py-0.5 rounded">
              {TOPIC_LABELS[promise.topic] ?? promise.topic}
            </span>
          )}
        </div>
        <div className="flex items-center gap-1.5 shrink-0">
          <SourceBadge tier={promise.tier} />
          <StatusBadge status={promise.status} />
        </div>
      </div>

      <Link href={`/promise/${promise.id}`} className="group">
        <p className="text-gray-900 text-sm leading-relaxed group-hover:text-blue-700 transition-colors line-clamp-3">
          {promise.text}
        </p>
      </Link>

      <div className="mt-3 flex items-center gap-2">
        <ArchiveLink archivedUrl={promise.archived_url} archivedDate={promise.archived_date} />
      </div>
    </article>
  );
}
