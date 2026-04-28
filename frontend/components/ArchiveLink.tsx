import { ExternalLink } from "lucide-react";

type Props = {
  archivedUrl: string;
  archivedDate?: string; // YYYYMMDD
  className?: string;
};

function formatDate(d: string): string {
  if (!d || d.length < 8) return d;
  return `${d.slice(6, 8)}/${d.slice(4, 6)}/${d.slice(0, 4)}`;
}

export default function ArchiveLink({ archivedUrl, archivedDate, className = "" }: Props) {
  if (!archivedUrl) return null;
  return (
    <a
      href={archivedUrl}
      target="_blank"
      rel="noopener noreferrer"
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-stone-100 hover:bg-stone-200 border border-stone-300 text-xs font-mono text-stone-700 hover:text-stone-900 transition-colors ${className}`}
      title="Ver página original arquivada no Arquivo.pt"
    >
      <ExternalLink size={11} />
      arquivo.pt
      {archivedDate && (
        <span className="text-stone-500">{formatDate(archivedDate)}</span>
      )}
    </a>
  );
}
