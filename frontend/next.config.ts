import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        // Proxy todas las rutas /api/** al backend FastAPI en el puerto 8000
        // EXCEPTO /api/auth/** que pertenece a NextAuth
        source: "/api/:path((?!auth).*)",
        destination: "http://localhost:8000/api/:path*",
      },
    ];
  },
};

export default nextConfig;
