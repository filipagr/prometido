import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    // Em produção, o backend está no Railway — NEXT_PUBLIC_API_URL aponta para lá
    // Em dev, proxy para localhost:8000
    const apiBase = process.env.API_URL ?? "http://localhost:8000";
    return [
      {
        source: "/api/:path*",
        destination: `${apiBase}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
