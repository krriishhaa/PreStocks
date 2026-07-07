/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: "standalone",
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/:path*`,
      },
    ];
  },
  async redirects() {
    return [
      {
        source: '/dashboard',
        destination: '/app/dashboard',
        permanent: true,
      },
      {
        source: '/learn',
        destination: '/app/learning',
        permanent: true,
      },
      {
        source: '/markets',
        destination: '/app/markets',
        permanent: true,
      },
    ];
  },
};

module.exports = nextConfig;
