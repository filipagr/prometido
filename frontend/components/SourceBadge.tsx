type Props = { tier: number; className?: string };

const TIER_LABELS: Record<number, { label: string; title: string; style: string }> = {
  1: { label: "Tier 1", title: "Site oficial do partido", style: "bg-emerald-100 text-emerald-800 border-emerald-200" },
  2: { label: "Tier 2", title: "Programa de governo", style: "bg-blue-100 text-blue-800 border-blue-200" },
  3: { label: "Tier 3", title: "Fonte jornalística", style: "bg-amber-100 text-amber-800 border-amber-200" },
};

export default function SourceBadge({ tier, className = "" }: Props) {
  const config = TIER_LABELS[tier] ?? { label: `Tier ${tier}`, title: "", style: "bg-gray-100 text-gray-600" };
  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded border text-xs font-medium ${config.style} ${className}`}
      title={config.title}
    >
      {config.label}
    </span>
  );
}
