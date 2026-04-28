type Props = { status: string; className?: string };

const STATUS_CONFIG: Record<string, { label: string; style: string }> = {
  archived:                      { label: "Arquivado",           style: "bg-gray-100 text-gray-600 border-gray-200" },
  corroborated:                  { label: "Corroborado",         style: "bg-sky-100 text-sky-800 border-sky-200" },
  evidence_of_implementation:    { label: "Evidência: cumprida", style: "bg-green-100 text-green-800 border-green-200" },
  evidence_of_non_implementation:{ label: "Evidência: não cumprida", style: "bg-red-100 text-red-800 border-red-200" },
  partial_implementation:        { label: "Cumprida parcialmente", style: "bg-orange-100 text-orange-800 border-orange-200" },
  untracked:                     { label: "Sem análise",         style: "bg-gray-50 text-gray-400 border-gray-200" },
};

export default function StatusBadge({ status, className = "" }: Props) {
  const config = STATUS_CONFIG[status] ?? { label: status, style: "bg-gray-100 text-gray-600 border-gray-200" };
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded border text-xs font-medium ${config.style} ${className}`}>
      {config.label}
    </span>
  );
}
