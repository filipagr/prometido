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
      title="Ver página original arquivada no Arquivo.pt"
      className={`inline-flex items-center gap-1 text-[11px] font-mono text-neutral-400 hover:text-neutral-700 transition-colors duration-150 ${className}`}
    >
      arquivo.pt
      {archivedDate && <span className="text-neutral-300">· {formatDate(archivedDate)}</span>}
      <span className="text-neutral-300 font-sans not-italic">↗</span>
    </a>
  );
}
