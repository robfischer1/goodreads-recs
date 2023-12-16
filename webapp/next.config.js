/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'images.gr-assets.com',
        port: '',
        pathname: '/books/**'
      }
    ]
  },
  reactStrictMode: true,
  experimental: {
    forceSwcTransforms: false,
  },
  output: 'standalone'
}

const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
})

module.exports = nextConfig
// module.exports = withBundleAnalyzer(nextConfig)
