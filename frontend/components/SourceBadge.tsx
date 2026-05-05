type Props = { tier: number; className?: string };

const TIER_CONFIG: Record<number, { label: string; title: string; color: string }> = {
  1: { label: "T1", title: "Site oficial do partido — máxima credibilidade", color: "#16a34a" },
  2: { label: "T2", title: "Programa de governo — fonte primária oficial",   color: "#2563eb" },
  3: { label: "T3", title: "Fonte jornalística — citação directa",           color: "#d97706" },
};

export default function SourceBadge({ tier, className = "" }: Props) {
  const config = TIER_CONFIG[tier] ?? { label: `T${tier}`, title: "", color: "#a3a3a3" };
  return (
    <span
      className={`inline-flex items-center text-[10px] font-semibold tabular-nums px-1.5 py-0.5 rounded border ${className}`}
      style={{ color: config.color, borderColor: `${config.color}40`, backgroundColor: `${config.color}0d` }}
      title={config.title}
    >
      {config.label}
    </span>
  );
}
