export default function ComoFunciona() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">Como funciona</h1>
      <p className="text-gray-600 mb-10">
        Metodologia do Prometido — transparência total sobre fontes, processo e limitações.
      </p>

      <section className="space-y-10">
        {/* Definição */}
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-3">O que é uma promessa</h2>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm text-blue-900 mb-3">
            <strong>Definição operacional:</strong> Declaração verificável com intenção futura explícita,
            atribuída directamente ao partido ou programa eleitoral, não parafraseada por jornalista.
          </div>
          <p className="text-sm text-gray-600">
            Incluímos: "vamos criar", "iremos implementar", "comprometemo-nos a", "será criado".
            Excluímos: retórica vaga ("queremos um Portugal melhor"), diagnósticos, críticas ao adversário.
          </p>
        </div>

        {/* Sistema de tiers */}
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-3">Hierarquia de fontes</h2>
          <div className="space-y-2">
            {[
              { tier: 1, label: "Tier 1 — Site oficial do partido", desc: "Programas eleitorais, press releases, páginas oficiais dos partidos. Fonte primária directa. Máxima credibilidade.", style: "border-emerald-200 bg-emerald-50 text-emerald-900" },
              { tier: 2, label: "Tier 2 — Programa de governo", desc: "Programas de governo publicados em portugal.gov.pt e similares. Fonte primária oficial pós-eleição.", style: "border-blue-200 bg-blue-50 text-blue-900" },
              { tier: 3, label: "Tier 3 — Fonte jornalística", desc: "Citações directas entre aspas em artigos do Público, Expresso, RTP, etc. Usado para corroboração e verificação de cumprimento.", style: "border-amber-200 bg-amber-50 text-amber-900" },
            ].map((t) => (
              <div key={t.tier} className={`border rounded-lg p-4 text-sm ${t.style}`}>
                <p className="font-semibold mb-1">{t.label}</p>
                <p>{t.desc}</p>
              </div>
            ))}
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Não usamos artigos que parafraseiam posições — risco de atribuição incorrecta.
          </p>
        </div>

        {/* Pipeline */}
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-3">Pipeline de extracção</h2>
          <div className="space-y-3 text-sm text-gray-700">
            {[
              { step: "1. Discovery", desc: "Arquivo.pt CDX API — descoberta de páginas arquivadas por domínio e janela temporal eleitoral." },
              { step: "2. Fetch", desc: "Fetch do HTML das páginas arquivadas via arquivo.pt/noFrame/replay. Extracção de texto limpo com trafilatura." },
              { step: "3. Extracção (Passo 1)", desc: "Claude API analisa cada página e extrai promessas candidatas com score de confiança. Texto longo dividido em chunks de 8000 caracteres." },
              { step: "4. Validação (Passo 2)", desc: "Segundo prompt independente valida cada promessa: é concreta? A atribuição é directa? Resultado: is_valid, validation_score, needs_human_review." },
              { step: "5. Curadoria humana", desc: "Apenas promessas com needs_human_review=true chegam à revisão manual (~30-50 de centenas). Os restantes são validados ou rejeitados automaticamente." },
            ].map((s) => (
              <div key={s.step} className="flex gap-3">
                <span className="font-mono font-semibold text-gray-900 shrink-0 w-36">{s.step}</span>
                <span>{s.desc}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Estados */}
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-3">Estados de uma promessa</h2>
          <p className="text-sm text-gray-600 mb-3">
            O Prometido usa uma linguagem de documentação, não de julgamento.
            Não dizemos que uma promessa foi "cumprida" ou "quebrada" — mostramos evidência arquivada e deixamos o utilizador concluir.
          </p>
          <div className="space-y-1.5 text-sm">
            {[
              { status: "Arquivado", desc: "Promessa encontrada em fonte primária (Tier 1/2). Automático." },
              { status: "Corroborado", desc: "Confirmada por citação directa em fonte jornalística (Tier 3). Automático." },
              { status: "Evidência: cumprida", desc: "Link arquivado de notícia ou página governamental que confirma implementação. Curadoria manual." },
              { status: "Evidência: não cumprida", desc: "Link arquivado de cobertura jornalística que reporta não-cumprimento. Curadoria manual." },
              { status: "Cumprida parcialmente", desc: "Evidência de implementação parcial. Curadoria manual." },
            ].map((s) => (
              <div key={s.status} className="flex gap-2">
                <span className="font-medium text-gray-900 shrink-0 w-44">{s.status}</span>
                <span className="text-gray-600">{s.desc}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Limitações */}
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-3">Limitações conhecidas</h2>
          <ul className="text-sm text-gray-600 space-y-2 list-disc pl-4">
            <li>
              <strong>BE/2005:</strong> bloco.org não foi crawlado pelo Arquivo.pt na janela eleitoral de 2005.
              Sem programa eleitoral Tier 1 disponível para esta eleição.
            </li>
            <li>
              A cobertura do arquivo varia por partido e eleição — partidos mais recentes
              (Chega, IL, Livre, PAN) têm histórico mais curto.
            </li>
            <li>
              A extracção automática tem uma taxa de erro estimada de 5-10%.
              Promessas de baixa confiança são marcadas e revistas manualmente.
            </li>
            <li>
              Verificação de cumprimento (Tier 3) é manual e limitada a 10-15 casos demonstrativos no MVP.
              A grande maioria das promessas está marcada como "sem análise".
            </li>
          </ul>
        </div>

        {/* Arquivo.pt */}
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-5">
          <h2 className="font-semibold text-gray-900 mb-2">Porquê o Arquivo.pt</h2>
          <p className="text-sm text-gray-600">
            Partidos apagam programas eleitorais depois das eleições. Governos redesenham sites.
            O Arquivo.pt é o único lugar onde estas páginas continuam acessíveis.
            Todas as fontes do Prometido são links directos para páginas congeladas no tempo —
            com o toolbar do arquivo visível. O utilizador pode verificar por si.
          </p>
        </div>
      </section>
    </div>
  );
}
