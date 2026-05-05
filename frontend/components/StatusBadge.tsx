type Props = { status: string; className?: string };

const STATUS_CONFIG: Record<string, { label: string; color: string }> = {
  archived:                       { label: "Arquivado",             color: "#a3a3a3" },
  corroborated:                   { label: "Corroborado",           color: "#38bdf8" },
  evidence_of_implementation:     { label: "Cumprida",              color: "#22c55e" },
  evidence_of_non_implementation: { label: "Não cumprida",          color: "#f87171" },
  partial_implementation:         { label: "Parcial",               color: "#fb923c" },
  untracked:                      { label: "Sem análise",           color: "#d4d4d4" },
};

export default function StatusBadge({ status, className = "" }: Props) {
  const config = STATUS_CONFIG[status] ?? { label: status, color: "#a3a3a3" };
  return (
    <span className={`inline-flex items-center gap-1.5 text-[11px] text-neutral-400 whitespace-nowrap ${className}`}>
      <span
        className="w-[5px] h-[5px] rounded-full shrink-0"
        style={{ backgroundColor: config.color }}
      />
      {config.label}
    </span>
  );
}
