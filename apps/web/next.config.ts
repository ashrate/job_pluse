import type { NextConfig } from "next";

// GitHub Pages 배포시 리포지토리 이름으로 변경
// 로컬 개발시에는 빈 문자열 사용
const isProd = process.env.NODE_ENV === 'production';
const basePath = isProd ? '/job_pluse' : '';

const nextConfig: NextConfig = {
  // GitHub Pages 정적 배포를 위한 설정
  output: 'export',

  // GitHub Pages는 /<repo-name>/ 경로 사용
  basePath: basePath,
  assetPrefix: basePath,

  // 정적 이미지 최적화 비활성화 (GitHub Pages에서 필요)
  images: {
    unoptimized: true,
  },

  // 트레일링 슬래시 추가 (GitHub Pages 호환성)
  trailingSlash: true,
};

export default nextConfig;
