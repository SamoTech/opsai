/** @type {import('next').NextConfig} */
const nextConfig = {
  // 'standalone' removed — not compatible with Vercel
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },
  // Allow images from external sources if needed
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: '**' },
    ],
  },
};

module.exports = nextConfig;
