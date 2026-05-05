import type { Metadata } from "next";
import { Geist } from "next/font/google";
import Link from "next/link";
import NavLinks from "@/components/NavLinks";
import "./globals.css";

const geist = Geist({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Prometido — O que prometeram. Onde está a prova.",
  description:
    "Pesquisa e compara promessas eleitorais de partidos políticos portugueses desde 2002, com fonte primária arquivada no Arquivo.pt.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt" className={geist.className}>
      <body className="min-h-screen flex flex-col bg-[#fafafa]">
        <header className="bg-white/90 backdrop-blur-md border-b border-neutral-200/80 sticky top-0 z-20">
          <div className="max-w-5xl mx-auto px-4 h-[52px] flex items-center justify-between">
            <Link href="/" className="flex items-center gap-2 group shrink-0">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none" className="shrink-0">
                <rect width="20" height="20" rx="5" fill="#2563EB"/>
                <rect x="5" y="5" width="4" height="10" rx="1.5" fill="white" fillOpacity="0.95"/>
                <rect x="11" y="5" width="4" height="6" rx="1.5" fill="white" fillOpacity="0.6"/>
              </svg>
              <span className="font-semibold text-[15px] text-neutral-900 tracking-[-0.01em] group-hover:text-blue-700 transition-colors duration-150">
                Prometido
              </span>
            </Link>
            <NavLinks />
          </div>
        </header>

        <main className="flex-1">{children}</main>

        <footer className="border-t border-neutral-200 bg-white mt-20">
          <div className="max-w-5xl mx-auto px-4 py-7">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-[13px] text-neutral-400">
              <p>
                Prometido usa o{" "}
                <a
                  href="https://arquivo.pt"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-neutral-500 underline underline-offset-2 hover:text-neutral-800 transition-colors"
                >
                  Arquivo.pt
                </a>{" "}
                como fonte primária · Candidatura ao Prémio Arquivo.pt 2026
              </p>
              <div className="flex items-center gap-4">
                <Link href="/como-funciona" className="hover:text-neutral-700 transition-colors underline underline-offset-2">
                  Metodologia
                </Link>
                <a
                  href="https://github.com/filipagr/prometido"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-neutral-700 transition-colors underline underline-offset-2"
                >
                  GitHub
                </a>
              </div>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
