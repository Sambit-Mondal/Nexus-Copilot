import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* Production-ready configuration */
  reactStrictMode: true,

  /* Enable optimized builds */
  swcMinify: true,

  /* API configuration */
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  },

  /* Headers for security and performance */
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          {
            key: "X-Content-Type-Options",
            value: "nosniff",
          },
          {
            key: "X-Frame-Options",
            value: "DENY",
          },
          {
            key: "X-XSS-Protection",
            value: "1; mode=block",
          },
          {
            key: "Referrer-Policy",
            value: "strict-origin-when-cross-origin",
          },
        ],
      },
    ];
  },

  /* Redirects for legacy routes */
  async redirects() {
    return [];
  },

  /* Image optimization */
  images: {
    unoptimized: true, // Disable image optimization for serverless
  },

  /* Compression */
  compress: true,

  /* PoweredByHeader */
  poweredByHeader: false,

  /* Generate ETags */
  generateEtags: true,

  /* Production source maps */
  productionBrowserSourceMaps: false,
};

export default nextConfig;
