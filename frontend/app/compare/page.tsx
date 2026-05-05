"use client";

import { useSearchParams, useRouter } from "next/navigation";
import { useEffect, useState, Suspense } from "react";
import { ChevronDown } from "lucide-react";
import Link from "next/link";
import { compare, getParties, getElections, type CompareResult, type Party, type Election } from "@/lib/api";
import StatusBadge from "@/components/StatusBadge";

const TOPICS = ["habitação","saúde","educação","economia","emprego","ambiente","segurança","justiça","transportes","tecnologia","administração pública","agricultura","cultura","desporto","outros"];

function Select({
  value,
  onChange,
  label,
  children,
}: {
  value: string;
  onChange: (v: string) => void;
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <p className="text-[11px] font-semibold text-neutral-600 uppercase tracking-widest mb-1.5">{label}</p>
      <div className="relative">
        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className={`appearance-none text-[13px] border rounded-lg pl-3 pr-8 py-2.5 bg-white focus:outline-none focus:ring-2 focus:ring-neutral-400/30 focus:border-neutral-400 cursor-pointer transition-all duration-150 font-medium min-w-[152px] ${
            value
              ? "border-neutral-400 text-neutral-900 bg-neutral-50"
              : "border-neutral-200 text-neutral-700 hover:border-neutral-300"
          }`}
        >
          {children}
        </select>
        <ChevronDown size={13} className="absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none text-neutral-500" />
      </div>
    </div>
  );
}

function partyAbbr(name: string): string {
  if (name.length <= 3) return name;
  return name.slice(0, 2);
}

function ComparePage() {
  const params = useSearchParams();
  const router = useRouter();

  const topic = params.get("topic") ?? "";
  const partiesParam = params.get("parties") ?? "";
  const election = params.get("election") ?? "";

  const [result, setResult] = useState<CompareResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [parties, setParties] = useState<Party[]>([]);
  const [elections, setElections] = useState<Election[]>([]);
  const [selectedParties, setSelectedParties] = useState<string[]>(
    partiesParam ? partiesParam.split(",") : []
  );

  useEffect(() => {
    getParties().then(setParties).catch(() => {});
    getElections().then(setElections).catch(() => {});
  }, []);

  useEffect(() => {
    if (!topic) return;
    setLoading(true);
    const p: Record<string, string> = { topic };
    if (selectedParties.length > 0) p.parties = selectedParties.join(",");
    if (election) p.election = election;
    compare(p).then(setResult).catch(() => setResult(null)).finally(() => setLoading(false));
  }, [topic, selectedParties.join(","), election]);

  function updateParam(key: string, value: string) {
    const next = new URLSearchParams(params.toString());
    if (value) next.set(key, value); else next.delete(key);
    router.push(`/compare?${next.toString()}`);
  }

  function toggleParty(pid: string) {
    const next = selectedParties.includes(pid)
      ? selectedParties.filter((p) => p !== pid)
      : [...selectedParties, pid];
    setSelectedParties(next);
    updateParam("parties", next.join(","));
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="mb-7">
        <h1 className="text-[22px] font-semibold text-neutral-950 tracking-[-0.02em] mb-1">Comparar promessas</h1>
        <p className="text-[13px] text-neutral-600">Compara o que diferentes partidos prometeram sobre o mesmo tema.</p>
      </div>

      {/* Controls */}
      <div className="bg-white border border-neutral-200 rounded-2xl p-5 mb-8 space-y-5">
        <div className="flex flex-wrap gap-5 items-end">
          <Select value={topic} onChange={(v) => updateParam("topic", v)} label="Tema">
            <option value="">Escolher tema…</option>
            {TOPICS.map((t) => <option key={t} value={t}>{t}</option>)}
          </Select>
          <Select value={election} onChange={(v) => updateParam("election", v)} label="Eleição">
            <option value="">Todas as eleições</option>
            {elections.map((e) => <option key={e.id} value={e.id}>{e.description}</option>)}
          </Select>
        </div>

        <div>
          <p className="text-[11px] font-semibold text-neutral-600 uppercase tracking-widest mb-2.5">
            Partidos
            {selectedParties.length > 0 && (
              <span className="ml-2 px-1.5 py-0.5 bg-neutral-100 text-neutral-700 rounded text-[10px] font-bold normal-case tracking-normal">
                {selectedParties.length}
              </span>
            )}
          </p>
          <div className="flex flex-wrap gap-1.5">
            {parties.map((p) => {
              const active = selectedParties.includes(p.id);
              return (
                <button
                  key={p.id}
                  onClick={() => toggleParty(p.id)}
                  className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[13px] font-semibold border transition-all duration-150 ${
                    active ? "text-white border-transparent shadow-sm" : "bg-white text-neutral-600 border-neutral-200 hover:border-neutral-300 hover:text-neutral-900"
                  }`}
                  style={active ? { backgroundColor: p.color, borderColor: p.color } : {}}
                >
                  {active && (
                    <span
                      className="w-4 h-4 rounded-md flex items-center justify-center text-[9px] font-bold shrink-0"
                      style={{ backgroundColor: "rgba(255,255,255,0.25)" }}
                    >
                      {partyAbbr(p.short_name)}
                    </span>
                  )}
                  {p.short_name}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Results */}
      {!topic ? (
        <div className="flex flex-col items-center justify-center py-24 text-center">
          <div className="w-10 h-10 rounded-xl bg-neutral-100 flex items-center justify-center mb-4">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round" className="text-neutral-500">
              <path d="M8 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h3"/>
              <path d="M16 3h3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-3"/>
              <line x1="12" y1="3" x2="12" y2="21"/>
            </svg>
          </div>
          <p className="text-[15px] font-medium text-neutral-800 mb-1">Escolhe um tema para começar</p>
          <p className="text-[13px] text-neutral-600 max-w-[260px] leading-relaxed">Selecciona um tema no menu acima para ver e comparar as promessas de cada partido.</p>
        </div>
      ) : loading ? (
        <div className="overflow-x-auto -mx-4 px-4 scrollbar-hide">
          <div className="flex gap-4 pb-4" style={{ minWidth: "840px" }}>
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="flex-1 space-y-2.5" style={{ minWidth: "260px" }}>
                <div className="skeleton h-5 w-20 rounded mb-4" />
                {Array.from({ length: 3 }).map((_, j) => (
                  <div key={j} className="bg-white border border-neutral-200 rounded-xl p-4 space-y-2">
                    <div className="skeleton h-3.5 w-full rounded" />
                    <div className="skeleton h-3.5 w-4/5 rounded" />
                    <div className="skeleton h-3.5 w-2/3 rounded" />
                    <div className="pt-2 border-t border-neutral-100 skeleton h-3 w-24 rounded" />
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>
      ) : !result || result.promise_count === 0 ? (
        <div className="py-16 text-center">
          <p className="text-[15px] font-medium text-neutral-700 mb-1">Nenhuma promessa encontrada</p>
          <p className="text-[13px] text-neutral-600">Tenta outro tema ou remove o filtro de eleição.</p>
        </div>
      ) : (
        <div className="fade-in">
          <p className="text-[12px] text-neutral-600 font-medium mb-5 tabular-nums">
            {result.promise_count.toLocaleString("pt")} promessa{result.promise_count !== 1 ? "s" : ""} sobre{" "}
            <span className="text-neutral-900 font-semibold">{topic}</span>
            {election && <span className="text-neutral-500"> · {elections.find((e) => e.id === election)?.description}</span>}
          </p>

          <div className="overflow-x-auto -mx-4 px-4 scrollbar-hide">
            <div className="flex gap-4 pb-6" style={{ minWidth: `${result.parties.length * 296}px` }}>
              {result.parties.map((party) => (
                <div key={party.id} className="flex-1 space-y-2.5" style={{ minWidth: "272px", maxWidth: "320px" }}>
                  <div
                    className="flex items-center gap-2 pb-2.5 border-b-[2px] pt-1"
                    style={{ borderColor: party.color }}
                  >
                    <span
                      className="w-6 h-6 rounded-lg flex items-center justify-center text-white font-bold shrink-0"
                      style={{
                        backgroundColor: party.color,
                        fontSize: party.short_name.length <= 2 ? "11px" : "9px",
                      }}
                    >
                      {partyAbbr(party.short_name)}
                    </span>
                    <span className="font-semibold text-[13px] tracking-tight" style={{ color: party.color }}>
                      {party.short_name}
                    </span>
                    <span className="text-[11px] text-neutral-500 ml-auto tabular-nums">{party.promises.length}</span>
                  </div>

                  {party.promises.map((p) => (
                    <div
                      key={p.id}
                      className="bg-white border border-neutral-200 rounded-xl p-4 hover:border-neutral-300 hover:shadow-[0_1px_4px_rgba(0,0,0,0.06)] transition-all duration-150 group/promise"
                    >
                      <Link href={`/promise/${p.id}`} className="block mb-3">
                        <p className="text-[13px] leading-[1.6] text-neutral-700 group-hover/promise:text-neutral-950 transition-colors duration-150">
                          {p.text}
                        </p>
                      </Link>
                      <div className="flex items-center gap-2 pt-2.5 border-t border-neutral-100">
                        <span className="text-[11px] text-neutral-500 tabular-nums font-medium">{p.election?.date?.slice(0, 4)}</span>
                        <StatusBadge status={p.status} />
                      </div>
                    </div>
                  ))}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function ComparePageWrapper() {
  return <Suspense><ComparePage /></Suspense>;
}
