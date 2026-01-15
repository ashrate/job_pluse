import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "JobPulse - 취업 지원 통합 관리 플랫폼",
  description: "여러 채널의 지원 현황을 통합 관리하고, 기업/공고 정보를 AI로 분석하며, 이력서를 진단하는 취업 지원 플랫폼",
  keywords: ["취업", "지원 관리", "이력서 분석", "AI", "Job Tracker"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
