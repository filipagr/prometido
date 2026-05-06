export default function ComoFunciona() {
  return (
    <div className="max-w-2xl mx-auto px-4 py-12">
      <div className="mb-10">
        <h1 className="text-[28px] font-semibold text-neutral-950 mb-2 tracking-[-0.02em]">Como funciona</h1>
        <p className="text-[14px] text-neutral-600 leading-relaxed">
          Metodologia do Arquivo Eleitoral — transparência total sobre fontes, processo e limitações.
        </p>
      </div>

      <section className="space-y-12">
        {/* O que é */}
        <div>
          <h2 className="text-[15px] font-semibold text-neutral-900 mb-3 tracking-[-0.01em]">O que é o Arquivo Eleitoral</h2>
          <p className="text-[13px] text-neutral-600 leading-relaxed mb-3">
            O Arquivo Eleitoral é uma base de dados de promessas eleitorais de partidos políticos portugueses,
            pesquisável e comparável, com ligação directa às fontes originais. Cobre 9 partidos e
            9 eleições legislativas de 2002 a 2025, com mais de 7.500 promessas extraídas.
          </p>
          <p className="text-[13px] text-neutral-600 leading-relaxed">
            A intenção futura é analisar, para os partidos que venceram eleições, se as promessas foram
            cumpridas — usando os registos do Arquivo.pt como fonte de evidência. Por agora, o foco
            está em tornar os programas eleitorais acessíveis e pesquisáveis: muitos partidos não
            disponibilizam programas antigos online, e o Arquivo.pt é frequentemente o único sítio
            onde esses documentos sobrevivem.
          </p>
        </div>

        {/* Arquivo.pt */}
        <div className="bg-white border border-neutral-200 rounded-2xl p-6">
          <h2 className="text-[15px] font-semibold text-neutral-900 mb-2.5 tracking-[-0.01em]">Porquê o Arquivo.pt</h2>
          <p className="text-[13px] text-neutral-600 leading-relaxed">
            Partidos apagam programas eleitorais depois das eleições. Governos redesenham sites.
            O Arquivo.pt é o único lugar onde muitas destas páginas continuam acessíveis,
            congeladas no tempo. Todas as fontes do Arquivo Eleitoral têm um link directo para a versão
            arquivada — o utilizador pode verificar por si, com o contexto original intacto.
          </p>
          <a
            href="https://arquivo.pt"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 mt-4 text-[13px] font-medium text-neutral-800 hover:text-neutral-950 transition-colors underline underline-offset-2"
          >
            Visitar arquivo.pt →
          </a>
        </div>

        {/* Definição */}
        <div>
          <h2 className="text-[15px] font-semibold text-neutral-900 mb-3 tracking-[-0.01em]">O que é uma promessa</h2>
          <div className="bg-neutral-50 border border-neutral-200 rounded-xl p-4 text-[13px] text-neutral-800 mb-3 leading-relaxed">
            <strong>Definição operacional:</strong> Declaração verificável com intenção futura explícita,
            atribuída directamente ao partido ou programa eleitoral.
          </div>
          <p className="text-[13px] text-neutral-600 leading-relaxed">
            Incluímos: &ldquo;vamos criar&rdquo;, &ldquo;iremos implementar&rdquo;, &ldquo;comprometemo-nos a&rdquo;.
            Excluímos: retórica vaga, diagnósticos, críticas ao adversário.
          </p>
        </div>

        {/* De onde vêm os dados */}
        <div>
          <h2 className="text-[15px] font-semibold text-neutral-900 mb-3 tracking-[-0.01em]">De onde vêm os dados</h2>
          <p className="text-[13px] text-neutral-600 leading-relaxed mb-4">
            Mais de 7.800 promessas extraídas de 9 partidos, cobrindo eleições legislativas de 2002 a 2025:
          </p>
          <div className="space-y-2">
            {[
              {
                label: "Arquivo.pt",
                desc: "Fonte principal. Para eleições de 2002 a 2019, usámos a CDX API para descobrir páginas arquivadas dos sites dos partidos durante os períodos eleitorais. Para 2019–2025, os programas existem maioritariamente como PDFs — a maioria está indexada directamente no Arquivo.pt.",
              },
              {
                label: "Ligação directa ao programa",
                desc: "Para programas não indexados pelo Arquivo.pt: CDS 2011 (fonte não oficial — tretas.org), Chega 2024 e 2025 (PDF no site do partido, carregado após a eleição), AD 2025 e BE 2024 (PDF no site do partido). Nestes casos o link aponta directamente para o documento original.",
              },
            ].map((t) => (
              <div key={t.label} className="bg-white border border-neutral-200 rounded-xl p-4 flex gap-4">
                <div>
                  <p className="text-[13px] font-semibold text-neutral-800 mb-0.5">{t.label}</p>
                  <p className="text-[13px] text-neutral-600 leading-relaxed">{t.desc}</p>
                </div>
              </div>
            ))}
          </div>
          <p className="text-[12px] text-neutral-500 mt-2.5 leading-relaxed">
            Todos os partidos com assento parlamentar estão incluídos. Coligações (AD em 2022–2025, CDU) são atribuídas ao partido principal (PSD e PCP, respectivamente).
          </p>
        </div>

        {/* Limitações */}
        <div>
          <h2 className="text-[15px] font-semibold text-neutral-900 mb-3 tracking-[-0.01em]">Limitações conhecidas</h2>
          <ul className="text-[13px] text-neutral-600 space-y-2.5 leading-relaxed">
            {[
              "<strong class=\"text-neutral-800\">CDS 2002:</strong> programa não encontrado em nenhuma fonte arquivada. Sem dados disponíveis.",
              "<strong class=\"text-neutral-800\">CDS 2011:</strong> PDF não indexado pelo Arquivo.pt. A fonte é um site não oficial (tretas.org) — documento autêntico mas sem arquivo institucional.",
              "<strong class=\"text-neutral-800\">Chega 2024 e 2025:</strong> PDFs carregados pelo partido após as eleições. O link aponta directamente para o PDF no site do partido — sem versão arquivada no Arquivo.pt.",
              "<strong class=\"text-neutral-800\">PS 2022, 2024 e 2025 · AD 2025:</strong> o Arquivo.pt não indexou o PDF do programa nestas eleições. O link aponta para a página de listagem de programas dos respectivos sites.",
              "<strong class=\"text-neutral-800\">BE 2025:</strong> o partido publicou apenas um manifesto de 2 páginas, sem programa completo.",
              "A cobertura varia por partido: Chega, IL, Livre e PAN têm histórico mais curto, a partir das eleições em que participaram pela primeira vez.",
              "A cobertura actual começa em 2002. A intenção é expandir para todas as legislativas desde 1975.",
              "A extracção automática tem uma taxa de erro estimada de 5–10%. Promessas de baixa confiança são marcadas internamente para revisão.",
            ].map((item, i) => (
              <li key={i} className="flex gap-2.5">
                <span className="text-neutral-400 shrink-0 mt-0.5">—</span>
                <span dangerouslySetInnerHTML={{ __html: item }} />
              </li>
            ))}
          </ul>
        </div>

      </section>
    </div>
  );
}
