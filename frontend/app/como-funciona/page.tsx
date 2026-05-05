export default function ComoFunciona() {
  return (
    <div className="max-w-2xl mx-auto px-4 py-12">
      <div className="mb-10">
        <h1 className="text-[28px] font-semibold text-neutral-950 mb-2 tracking-[-0.02em]">Como funciona</h1>
        <p className="text-[14px] text-neutral-600 leading-relaxed">
          Metodologia do Prometido — transparência total sobre fontes, processo e limitações.
        </p>
      </div>

      <section className="space-y-12">
        {/* O que é */}
        <div>
          <h2 className="text-[15px] font-semibold text-neutral-900 mb-3 tracking-[-0.01em]">O que é o Prometido</h2>
          <p className="text-[13px] text-neutral-600 leading-relaxed mb-3">
            O Prometido é uma base de dados de promessas eleitorais de partidos políticos portugueses,
            pesquisável e comparável, com ligação directa às fontes arquivadas. Cobre 9 partidos e
            9 eleições legislativas de 2002 a 2025, com mais de 7.500 promessas extraídas.
          </p>
          <p className="text-[13px] text-neutral-600 leading-relaxed">
            O projecto não avalia se as promessas foram ou não cumpridas — esse juízo é genuinamente
            difícil e subjectivo. O valor está em tornar os programas eleitorais acessíveis e pesquisáveis:
            muitos partidos não disponibilizam programas antigos online, e precisar do Arquivo.pt para
            aceder a um programa de 2009 demonstra exactamente o problema que este projecto resolve.
          </p>
        </div>

        {/* Definição */}
        <div>
          <h2 className="text-[15px] font-semibold text-neutral-900 mb-3 tracking-[-0.01em]">O que é uma promessa</h2>
          <div className="bg-neutral-50 border border-neutral-200 rounded-xl p-4 text-[13px] text-neutral-800 mb-3 leading-relaxed">
            <strong>Definição operacional:</strong> Declaração verificável com intenção futura explícita,
            atribuída directamente ao partido ou programa eleitoral, não parafraseada por jornalista.
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
            Usámos uma abordagem híbrida consoante o partido e a eleição:
          </p>
          <div className="space-y-2">
            {[
              {
                label: "Arquivo.pt CDX API",
                desc: "Para partidos históricos (PS, PSD, BE, PCP, CDS) nas eleições de 2005 a 2019. O Arquivo.pt faz crawls especiais em períodos eleitorais — os sites dos partidos dessas épocas estão preservados. Usámos a CDX API para descobrir páginas arquivadas e o endpoint de fetch para obter o texto.",
              },
              {
                label: "PDFs e Wayback Machine",
                desc: "Para partidos mais recentes (IL, Chega, Livre, PAN) e eleições de 2022-2025, os programas existem como PDFs. Alguns estão no Arquivo.pt, outros no Wayback Machine ou nos próprios sites. O link para o arquivo serve como evidência de origem.",
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
            Todos os partidos com assento parlamentar estão incluídos. Coligações (AD, CDU) são atribuídas ao partido principal.
          </p>
        </div>

        {/* Pipeline */}
        <div>
          <h2 className="text-[15px] font-semibold text-neutral-900 mb-5 tracking-[-0.01em]">Pipeline de extracção</h2>
          <div className="space-y-0">
            {[
              { n: "1", label: "Discovery",    desc: "Identificação das páginas ou PDFs com os programas eleitorais, via Arquivo.pt CDX API, Wayback Machine ou fontes directas." },
              { n: "2", label: "Fetch",        desc: "Download do HTML ou PDF. Extracção de texto limpo com trafilatura (HTML) ou pypdf (PDF). Textos longos divididos em chunks de 8.000 caracteres." },
              { n: "3", label: "Extracção",    desc: "Claude Sonnet analisa cada chunk e extrai promessas com score de confiança. Prompt optimizado para português e para o contexto de programas eleitorais." },
              { n: "4", label: "Validação",    desc: "Claude Haiku valida cada promessa extraída: é concreta? A atribuição é directa? Apenas promessas com validação positiva entram na base de dados." },
              { n: "5", label: "Curadoria",    desc: "Casos ambíguos marcados com needs_human_review passam por revisão manual. Para PDFs de partidos recentes, a extracção foi feita directamente com Claude via sessão interactiva." },
            ].map((s, i, arr) => (
              <div key={s.n} className="flex gap-4">
                <div className="flex flex-col items-center shrink-0">
                  <div className="w-7 h-7 rounded-full bg-neutral-100 border border-neutral-200 flex items-center justify-center text-[11px] font-semibold text-neutral-600">
                    {s.n}
                  </div>
                  {i < arr.length - 1 && <div className="w-px flex-1 bg-neutral-200 my-1.5" />}
                </div>
                <div className="pb-5">
                  <p className="text-[13px] font-semibold text-neutral-800 mb-0.5">{s.label}</p>
                  <p className="text-[13px] text-neutral-600 leading-relaxed">{s.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Estados */}
        <div>
          <h2 className="text-[15px] font-semibold text-neutral-900 mb-2 tracking-[-0.01em]">Estados de uma promessa</h2>
          <p className="text-[13px] text-neutral-600 mb-4 leading-relaxed">
            O Prometido usa uma linguagem de documentação, não de julgamento.
            Não dizemos que uma promessa foi cumprida ou quebrada — mostramos a evidência e deixamos o utilizador concluir.
          </p>
          <div className="divide-y divide-neutral-100 border border-neutral-200 rounded-xl overflow-hidden">
            {[
              { status: "Arquivado",           desc: "Encontrada em fonte primária. Estado por omissão após extracção." },
              { status: "Corroborado",         desc: "Confirmada por citação directa em fonte jornalística arquivada." },
              { status: "Evidência: cumprida", desc: "Link arquivado que documenta a implementação." },
              { status: "Evidência: não cumprida", desc: "Link arquivado que reporta não-cumprimento." },
              { status: "Parcialmente cumprida", desc: "Evidência de implementação parcial." },
            ].map((s) => (
              <div key={s.status} className="flex gap-4 px-4 py-3 bg-white text-[13px]">
                <span className="font-semibold text-neutral-800 shrink-0 w-44">{s.status}</span>
                <span className="text-neutral-600 leading-relaxed">{s.desc}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Limitações */}
        <div>
          <h2 className="text-[15px] font-semibold text-neutral-900 mb-3 tracking-[-0.01em]">Limitações conhecidas</h2>
          <ul className="text-[13px] text-neutral-600 space-y-2.5 leading-relaxed">
            {[
              "<strong class=\"text-neutral-800\">BE 2005:</strong> bloco.org não foi crawlado pelo Arquivo.pt na janela eleitoral de 2005. Sem programa disponível.",
              "<strong class=\"text-neutral-800\">BE 2025:</strong> o partido publicou apenas um manifesto de 2 páginas, sem programa completo — reflecte a opção do partido.",
              "A cobertura varia por partido e eleição. Partidos recentes (Chega, IL, Livre, PAN) têm histórico mais curto, correspondente às eleições em que participaram.",
              "A extracção automática tem uma taxa de erro estimada de 5–10%. Promessas de baixa confiança são marcadas internamente para revisão.",
              "Verificação de cumprimento está fora do âmbito desta versão.",
            ].map((item, i) => (
              <li key={i} className="flex gap-2.5">
                <span className="text-neutral-400 shrink-0 mt-0.5">—</span>
                <span dangerouslySetInnerHTML={{ __html: item }} />
              </li>
            ))}
          </ul>
        </div>

        {/* Arquivo.pt */}
        <div className="bg-white border border-neutral-200 rounded-2xl p-6">
          <h2 className="text-[15px] font-semibold text-neutral-900 mb-2.5 tracking-[-0.01em]">Porquê o Arquivo.pt</h2>
          <p className="text-[13px] text-neutral-600 leading-relaxed">
            Partidos apagam programas eleitorais depois das eleições. Governos redesenham sites.
            O Arquivo.pt é o único lugar onde muitas destas páginas continuam acessíveis,
            congeladas no tempo. Todas as fontes do Prometido têm um link directo para a versão
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
      </section>
    </div>
  );
}
