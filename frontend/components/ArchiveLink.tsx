type Props = {
  archivedUrl: string;
  archivedDate?: string; // YYYYMMDD
  sourceType?: "arquivo_pt" | "direct";
  className?: string;
};

function formatDate(d: string): string {
  if (!d || d.length < 8) return d;
  return `${d.slice(6, 8)}/${d.slice(4, 6)}/${d.slice(0, 4)}`;
}

function getDomain(url: string): string {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return url;
  }
}

export default function ArchiveLink({ archivedUrl, archivedDate, sourceType = "arquivo_pt", className = "" }: Props) {
  if (!archivedUrl) return null;

  const isDirect = sourceType === "direct";
  const label = isDirect ? getDomain(archivedUrl) : "arquivo.pt";

  return (
    <a
      href={archivedUrl}
      target="_blank"
      rel="noopener noreferrer"
      title={
        isDirect
          ? "Fonte não arquivada oficialmente — este documento pode deixar de estar disponível"
          : "Ver página original arquivada no Arquivo.pt"
      }
      className={`inline-flex items-center gap-1 text-[11px] font-mono transition-colors duration-150 ${
        isDirect
          ? "text-amber-600 hover:text-amber-800"
          : "text-neutral-600 hover:text-neutral-900"
      } ${className}`}
    >
      {isDirect && (
        <span className="font-sans not-italic text-amber-500" aria-label="fonte não arquivada">⚠</span>
      )}
      {label}
      {archivedDate && (
        <span className={isDirect ? "text-amber-400" : "text-neutral-500"}>
          · {formatDate(archivedDate)}
        </span>
      )}
      <span className={`font-sans not-italic ${isDirect ? "text-amber-400" : "text-neutral-500"}`}>↗</span>
    </a>
  );
}
