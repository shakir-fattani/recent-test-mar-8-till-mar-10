import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  async rewrites() {
    return [
      {
        // Backend API proxy
        source: '/api/:path*',
        destination: process.env.NEXT_PUBLIC_API_URL || '/api/v1/:path*',
      },
    ];
  },
  images: {
    domains: ['localhost'],
  },
};

export default nextConfig;
