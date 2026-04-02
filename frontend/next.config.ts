import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // อนุญาตให้ IP ของเครื่องคุณเชื่อมต่อระบบ Dev ได้
  allowedDevOrigins: ['192.168.0.104'],
};

export default nextConfig;