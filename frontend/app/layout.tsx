import type { Metadata } from "next";
import { Geist } from "next/font/google";
import Link from "next/link";
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
      <body className="min-h-screen flex flex-col">
        <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
          <div className="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
            <Link href="/" className="font-bold text-lg text-gray-900 tracking-tight hover:text-blue-700 transition-colors">
              Prometido
            </Link>
            <nav className="flex items-center gap-6 text-sm text-gray-600">
              <Link href="/compare" className="hover:text-gray-900 transition-colors">
                Comparar
              </Link>
              <Link href="/search" className="hover:text-gray-900 transition-colors">
                Pesquisar
              </Link>
              <Link href="/como-funciona" className="hover:text-gray-900 transition-colors">
                Como funciona
              </Link>
            </nav>
          </div>
        </header>

        <main className="flex-1">{children}</main>

        <footer className="border-t border-gray-200 bg-white mt-16">
          <div className="max-w-5xl mx-auto px-4 py-8 flex items-center justify-between text-sm text-gray-500">
            <p>
              Prometido usa o{" "}
              <a href="https://arquivo.pt" target="_blank" rel="noopener noreferrer" className="underline hover:text-gray-700">
                Arquivo.pt
              </a>{" "}
              como fonte primária. Candidatura ao Prémio Arquivo.pt 2026.
            </p>
            <Link href="/como-funciona" className="hover:text-gray-700 underline">
              Metodologia
            </Link>
          </div>
        </footer>
      </body>
    </html>
  );
}
