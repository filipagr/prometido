import Link from "next/link";
import type { PromiseItem } from "@/lib/api";
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
  const metaParts: React.ReactNode[] = [];

  if (showParty) {
    metaParts.push(
      <span key="party" className="font-semibold" style={{ color: promise.party.color }}>
        {promise.party.short_name}
      </span>
    );
  }
  if (showElection && promise.election.date) {
    metaParts.push(
      <span key="year" className="tabular-nums text-neutral-400">
        {promise.election.date.slice(0, 4)}
      </span>
    );
  }
  if (promise.topic) {
    metaParts.push(
      <span key="topic" className="text-neutral-400">
        {TOPIC_LABELS[promise.topic] ?? promise.topic}
      </span>
    );
  }

  return (
    <article className="bg-white border border-neutral-200 rounded-xl overflow-hidden hover:border-neutral-300 hover:shadow-[0_1px_4px_rgba(0,0,0,0.06)] transition-all duration-150 relative group/card">
      {/* 2px party accent bar */}
      <div
        className="absolute left-0 top-0 bottom-0 w-[2px]"
        style={{ backgroundColor: promise.party.color }}
      />

      <div className="px-4 pt-3.5 pb-3 pl-[18px]">
        {/* Compact metadata line */}
        <div className="flex items-center justify-between gap-3 mb-2">
          <div className="flex items-center gap-1.5 text-[12px] min-w-0 flex-1">
            {metaParts.map((part, i) => (
              <span key={i} className="flex items-center gap-1.5">
                {i > 0 && <span className="text-neutral-200 select-none">·</span>}
                {part}
              </span>
            ))}
          </div>
          <StatusBadge status={promise.status} />
        </div>

        {/* Promise text */}
        <Link href={`/promise/${promise.id}`} className="block">
          <p className="text-[13.5px] leading-[1.6] text-neutral-700 group-hover/card:text-blue-700 transition-colors duration-150 line-clamp-3">
            {promise.text}
          </p>
        </Link>

        {/* Footer */}
        <div className="mt-2.5">
          <ArchiveLink archivedUrl={promise.archived_url} archivedDate={promise.archived_date} />
        </div>
      </div>
    </article>
  );
}
