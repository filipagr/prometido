type Props = { tier: number; className?: string };

const TIER_CONFIG: Record<number, { label: string; title: string }> = {
  1: { label: "T1", title: "Site oficial do partido" },
  2: { label: "T2", title: "Programa de governo"    },
  3: { label: "T3", title: "Fonte jornalística"     },
};

export default function SourceBadge({ tier, className = "" }: Props) {
  const config = TIER_CONFIG[tier] ?? { label: `T${tier}`, title: "" };
  return (
    <span
      className={`inline-flex items-center text-[10px] font-semibold tabular-nums px-1.5 py-0.5 rounded border border-neutral-200 bg-neutral-50 text-neutral-600 ${className}`}
      title={config.title}
    >
      {config.label}
    </span>
  );
}
