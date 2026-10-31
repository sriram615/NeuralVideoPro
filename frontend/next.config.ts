import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactCompiler: true,
  images: {
    remotePatterns: [
      {
        protocol: "http",
        hostname: "localhost",
        port: "8000",
        pathname: "/static/**",
      },
    ],
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:8000/api/:path*",
      },
      {
        source: "/static/frames/:path*",
        destination: "http://localhost:8000/static/frames/:path*",
      },
      {
        source: "/static/videos/:path*",
        destination: "http://localhost:8000/static/videos/:path*",
      },
    ];
  },
};

export default nextConfig;
