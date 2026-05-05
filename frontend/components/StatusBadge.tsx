type Props = { status: string; className?: string };

const STATUS_CONFIG: Record<string, { label: string; color: string }> = {
  archived:                       { label: "Arquivado",             color: "#737373" },
  corroborated:                   { label: "Corroborado",           color: "#404040" },
  evidence_of_implementation:     { label: "Cumprida",              color: "#16a34a" },
  evidence_of_non_implementation: { label: "Não cumprida",          color: "#dc2626" },
  partial_implementation:         { label: "Parcial",               color: "#d97706" },
  untracked:                      { label: "Sem análise",           color: "#a3a3a3" },
};

export default function StatusBadge({ status, className = "" }: Props) {
  const config = STATUS_CONFIG[status] ?? { label: status, color: "#737373" };
  return (
    <span className={`inline-flex items-center gap-1.5 text-[11px] text-neutral-600 whitespace-nowrap ${className}`}>
      <span
        className="w-[5px] h-[5px] rounded-full shrink-0"
        style={{ backgroundColor: config.color }}
      />
      {config.label}
    </span>
  );
}
