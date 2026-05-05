"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/compare", label: "Comparar" },
  { href: "/search", label: "Pesquisar" },
  { href: "/como-funciona", label: "Como funciona" },
];

export default function NavLinks() {
  const pathname = usePathname();

  function isActive(href: string) {
    return pathname === href || (href !== "/" && pathname.startsWith(href));
  }

  return (
    <nav className="flex items-center gap-0.5 text-sm">
      {links.map(({ href, label }) => (
        <Link
          key={href}
          href={href}
          className={`px-3 py-1.5 rounded-lg transition-colors duration-150 ${
            isActive(href)
              ? "bg-neutral-100 text-neutral-900 font-medium"
              : "text-neutral-500 hover:text-neutral-800 hover:bg-neutral-50"
          }`}
        >
          {label}
        </Link>
      ))}
    </nav>
  );
}
