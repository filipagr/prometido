"use client";

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { Search } from "lucide-react";

type Props = {
  defaultValue?: string;
  placeholder?: string;
  autoFocus?: boolean;
};

export default function SearchBar({
  defaultValue = "",
  placeholder = "Pesquisar promessas… habitação, SNS, salário mínimo",
  autoFocus = false,
}: Props) {
  const [value, setValue] = useState(defaultValue);
  const router = useRouter();
  const inputRef = useRef<HTMLInputElement>(null);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const q = value.trim();
    if (!q) return;
    router.push(`/search?q=${encodeURIComponent(q)}`);
  }

  return (
    <form onSubmit={handleSubmit} className="relative w-full">
      <Search
        size={15}
        className="absolute left-4 top-1/2 -translate-y-1/2 text-neutral-400 pointer-events-none"
      />
      <input
        ref={inputRef}
        type="search"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder={placeholder}
        autoFocus={autoFocus}
        className="w-full pl-10 pr-28 py-3.5 text-sm border border-neutral-200 rounded-xl bg-white shadow-[0_1px_3px_rgba(0,0,0,0.05)] focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 placeholder:text-neutral-400 transition-all duration-150"
      />
      <button
        type="submit"
        className="absolute right-2 top-1/2 -translate-y-1/2 px-3.5 py-2 bg-blue-600 hover:bg-blue-700 active:scale-[0.97] text-white text-[13px] font-medium rounded-lg transition-all duration-150 shadow-sm"
      >
        Pesquisar
      </button>
    </form>
  );
}
