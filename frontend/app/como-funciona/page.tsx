export default function ComoFunciona() {
  return (
    <div className="max-w-2xl mx-auto px-4 py-12">
      <div className="mb-10">
        <h1 className="text-[28px] font-semibold text-neutral-950 mb-2 tracking-[-0.02em]">Como funciona</h1>
        <p className="text-[14px] text-neutral-500 leading-relaxed">
          Metodologia do Prometido — transparência total sobre fontes, processo e limitações.
        </p>
      </div>

      <section className="space-y-12">
        {/* Definição */}
        <div>
          <h2 className="text-[15px] font-semibold text-neutral-900 mb-3 tracking-[-0.01em]">O que é uma promessa</h2>
          <div className="bg-blue-50 border border-blue-100 rounded-xl p-4 text-[13px] text-blue-900 mb-3 leading-relaxed">
            <strong>Definição operacional:</strong> Declaração verificável com intenção futura explícita,
            atribuída directamente ao partido ou programa eleitoral, não parafraseada por jornalista.
          </div>
          <p className="text-[13px] text-neutral-500 leading-relaxed">
            Incluímos: &ldquo;vamos criar&rdquo;, &ldquo;iremos implementar&rdquo;, &ldquo;comprometemo-nos a&rdquo;.
            Excluímos: retórica vaga, diagnósticos, críticas ao adversário.
          </p>
        </div>

        {/* Hierarquia */}
        <div>
          <h2 className="text-[15px] font-semibold text-neutral-900 mb-3 tracking-[-0.01em]">Hierarquia de fontes</h2>
          <div className="space-y-2">
            {[
              { tier: 1, label: "Tier 1", sublabel: "Site oficial do partido", desc: "Programas eleitorais, press releases, páginas oficiais. Fonte primária directa. Máxima credibilidade.", color: "#16a34a" },
              { tier: 2, label: "Tier 2", sublabel: "Programa de governo",     desc: "Programas de governo publicados em portugal.gov.pt e similares. Fonte primária oficial pós-eleição.",    color: "#2563eb" },
              { tier: 3, label: "Tier 3", sublabel: "Fonte jornalística",      desc: "Citações directas entre aspas em artigos do Público, Expresso, RTP. Para corroboração e verificação.",   color: "#d97706" },
            ].map((t) => (
              <div key={t.tier} className="bg-white border border-neutral-200 rounded-xl p-4 flex gap-4">
                <span
                  className="text-[11px] font-semibold px-1.5 py-0.5 rounded border shrink-0 mt-0.5 h-fit tabular-nums"
                  style={{ color: t.color, borderColor: `${t.color}40`, backgroundColor: `${t.color}0d` }}
                >
                  {t.label}
                </span>
                <div>
                  <p className="text-[13px] font-semibold text-neutral-800 mb-0.5">{t.sublabel}</p>
                  <p className="text-[13px] text-neutral-500 leading-relaxed">{t.desc}</p>
                </div>
              </div>
            ))}
          </div>
          <p className="text-[12px] text-neutral-400 mt-2.5 leading-relaxed">
            Não usamos artigos que parafraseiam posições — risco de atribuição incorrecta.
          </p>
        </div>

        {/* Pipeline */}
        <div>
          <h2 className="text-[15px] font-semibold text-neutral-900 mb-5 tracking-[-0.01em]">Pipeline de extracção</h2>
          <div className="space-y-0">
            {[
              { n: "1", label: "Discovery",    desc: "Arquivo.pt CDX API — descoberta de páginas arquivadas por domínio e janela temporal eleitoral." },
              { n: "2", label: "Fetch",        desc: "Fetch do HTML das páginas arquivadas. Extracção de texto limpo com trafilatura." },
              { n: "3", label: "Extracção",    desc: "Claude API analisa cada página e extrai promessas com score de confiança. Texto longo dividido em chunks de 8.000 caracteres." },
              { n: "4", label: "Validação",    desc: "Segundo prompt independente valida cada promessa: é concreta? A atribuição é directa? Resultado: is_valid, validation_score." },
              { n: "5", label: "Curadoria",    desc: "Apenas promessas com needs_human_review=true chegam à revisão manual (~30–50 de centenas)." },
            ].map((s, i, arr) => (
              <div key={s.n} className="flex gap-4">
                <div className="flex flex-col items-center shrink-0">
                  <div className="w-7 h-7 rounded-full bg-neutral-100 border border-neutral-200 flex items-center justify-center text-[11px] font-semibold text-neutral-500">
                    {s.n}
                  </div>
                  {i < arr.length - 1 && <div className="w-px flex-1 bg-neutral-200 my-1.5" />}
                </div>
                <div className="pb-5">
                  <p className="text-[13px] font-semibold text-neutral-800 mb-0.5">{s.label}</p>
                  <p className="text-[13px] text-neutral-500 leading-relaxed">{s.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Estados */}
        <div>
          <h2 className="text-[15px] font-semibold text-neutral-900 mb-2 tracking-[-0.01em]">Estados de uma promessa</h2>
          <p className="text-[13px] text-neutral-500 mb-4 leading-relaxed">
            O Prometido usa uma linguagem de documentação, não de julgamento.
            Não dizemos que uma promessa foi &ldquo;cumprida&rdquo; ou &ldquo;quebrada&rdquo; — mostramos evidência e deixamos o utilizador concluir.
          </p>
          <div className="divide-y divide-neutral-100 border border-neutral-200 rounded-xl overflow-hidden">
            {[
              { status: "Arquivado",           desc: "Encontrada em fonte primária (T1/T2). Automático." },
              { status: "Corroborado",         desc: "Confirmada por citação directa em fonte jornalística (T3). Automático." },
              { status: "Evidência: cumprida", desc: "Link arquivado que confirma implementação. Curadoria manual." },
              { status: "Evidência: não cumprida", desc: "Link arquivado que reporta não-cumprimento. Curadoria manual." },
              { status: "Parcialmente cumprida", desc: "Evidência de implementação parcial. Curadoria manual." },
            ].map((s) => (
              <div key={s.status} className="flex gap-4 px-4 py-3 bg-white text-[13px]">
                <span className="font-semibold text-neutral-700 shrink-0 w-44">{s.status}</span>
                <span className="text-neutral-500 leading-relaxed">{s.desc}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Limitações */}
        <div>
          <h2 className="text-[15px] font-semibold text-neutral-900 mb-3 tracking-[-0.01em]">Limitações conhecidas</h2>
          <ul className="text-[13px] text-neutral-500 space-y-2.5 leading-relaxed">
            {[
              "<strong class=\"text-neutral-700\">BE/2005:</strong> bloco.org não foi crawlado pelo Arquivo.pt na janela eleitoral de 2005. Sem Tier 1 disponível.",
              "A cobertura varia por partido e eleição — partidos recentes (Chega, IL, Livre, PAN) têm histórico mais curto.",
              "A extracção automática tem uma taxa de erro estimada de 5–10%. Promessas de baixa confiança são marcadas para revisão.",
              "Verificação de cumprimento é manual e limitada a 10–15 casos demonstrativos no MVP.",
            ].map((item, i) => (
              <li key={i} className="flex gap-2.5">
                <span className="text-neutral-300 shrink-0 mt-0.5">—</span>
                <span dangerouslySetInnerHTML={{ __html: item }} />
              </li>
            ))}
          </ul>
        </div>

        {/* Arquivo.pt */}
        <div className="bg-white border border-neutral-200 rounded-2xl p-6">
          <h2 className="text-[15px] font-semibold text-neutral-900 mb-2.5 tracking-[-0.01em]">Porquê o Arquivo.pt</h2>
          <p className="text-[13px] text-neutral-500 leading-relaxed">
            Partidos apagam programas eleitorais depois das eleições. Governos redesenham sites.
            O Arquivo.pt é o único lugar onde estas páginas continuam acessíveis.
            Todas as fontes do Prometido são links directos para páginas congeladas no tempo,
            com o toolbar do arquivo visível. O utilizador pode verificar por si.
          </p>
          <a
            href="https://arquivo.pt"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 mt-4 text-[13px] font-medium text-blue-600 hover:text-blue-800 transition-colors"
          >
            Visitar arquivo.pt →
          </a>
        </div>
      </section>
    </div>
  );
}
