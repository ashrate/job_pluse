'use client';

import Link from 'next/link';
import { useState, useEffect } from 'react';
import styles from './page.module.css';

export default function LandingPage() {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setIsVisible(true);
  }, []);

  return (
    <div className={styles.landing}>
      {/* Navigation */}
      <nav className={styles.nav}>
        <div className={styles.navContent}>
          <div className={styles.logo}>
            <div className={styles.logoIcon}>🚀</div>
            <span>JobPulse</span>
          </div>
          <div className={styles.navLinks}>
            <a href="#features" className={styles.navLink}>기능</a>
            <a href="#how-it-works" className={styles.navLink}>사용방법</a>
            <a href="#pricing" className={styles.navLink}>가격</a>
          </div>
          <Link href="/dashboard" className={`btn btn-primary ${styles.navCta}`}>
            시작하기
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section className={`${styles.hero} ${isVisible ? styles.visible : ''}`}>
        <div className={styles.heroContent}>
          <div className={styles.heroBadge}>
            <span>✨ AI 기반 취업 지원 플랫폼</span>
          </div>
          <h1 className={styles.heroTitle}>
            취업 지원,<br />
            <span className="text-gradient">더 스마트하게</span>
          </h1>
          <p className={styles.heroDescription}>
            여러 채널의 지원 현황을 한 곳에서 관리하고,<br />
            AI가 이력서를 진단하고 기업 정보를 요약해드립니다.
          </p>
          <div className={styles.heroButtons}>
            <Link href="/dashboard" className="btn btn-primary btn-lg">
              무료로 시작하기 →
            </Link>
            <a href="#demo" className="btn btn-secondary btn-lg">
              데모 보기
            </a>
          </div>
          <div className={styles.heroStats}>
            <div className={styles.heroStat}>
              <span className={styles.heroStatValue}>10K+</span>
              <span className={styles.heroStatLabel}>활성 사용자</span>
            </div>
            <div className={styles.heroDivider}></div>
            <div className={styles.heroStat}>
              <span className={styles.heroStatValue}>50K+</span>
              <span className={styles.heroStatLabel}>지원 관리</span>
            </div>
            <div className={styles.heroDivider}></div>
            <div className={styles.heroStat}>
              <span className={styles.heroStatValue}>95%</span>
              <span className={styles.heroStatLabel}>만족도</span>
            </div>
          </div>
        </div>
        <div className={styles.heroVisual}>
          <div className={styles.dashboardPreview}>
            <div className={styles.previewHeader}>
              <div className={styles.previewDots}>
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
            <div className={styles.previewContent}>
              <div className={styles.previewSidebar}></div>
              <div className={styles.previewMain}>
                <div className={styles.previewCards}>
                  <div className={styles.previewCard}></div>
                  <div className={styles.previewCard}></div>
                  <div className={styles.previewCard}></div>
                </div>
                <div className={styles.previewBoard}>
                  <div className={styles.previewColumn}></div>
                  <div className={styles.previewColumn}></div>
                  <div className={styles.previewColumn}></div>
                  <div className={styles.previewColumn}></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className={styles.features}>
        <div className={styles.sectionHeader}>
          <h2 className={styles.sectionTitle}>
            취업 준비의 <span className="text-gradient">새로운 기준</span>
          </h2>
          <p className={styles.sectionDescription}>
            지원 관리부터 이력서 진단까지, 모든 것을 한 곳에서
          </p>
        </div>
        <div className={styles.featuresGrid}>
          <div className={styles.featureCard}>
            <div className={styles.featureIcon}>📋</div>
            <h3>지원현황 통합 관리</h3>
            <p>
              칸반 보드로 모든 지원 현황을 한눈에 파악하세요.
              관심 → 지원 → 면접 → 합격까지 진행 상황을 추적합니다.
            </p>
          </div>
          <div className={styles.featureCard}>
            <div className={styles.featureIcon}>🤖</div>
            <h3>AI 이력서 진단</h3>
            <p>
              ATS 친화도, 임팩트 표현, 키워드 매칭까지
              AI가 이력서를 분석하고 개선점을 제안합니다.
            </p>
          </div>
          <div className={styles.featureCard}>
            <div className={styles.featureIcon}>🏢</div>
            <h3>기업 정보 요약</h3>
            <p>
              지원할 기업의 정보를 RAG 기반으로 요약하고
              출처와 함께 신뢰할 수 있는 정보를 제공합니다.
            </p>
          </div>
          <div className={styles.featureCard}>
            <div className={styles.featureIcon}>📧</div>
            <h3>Gmail 연동</h3>
            <p>
              Gmail에서 자동으로 지원 관련 이메일을 파싱하여
              지원 현황을 자동 업데이트합니다.
            </p>
          </div>
          <div className={styles.featureCard}>
            <div className={styles.featureIcon}>📅</div>
            <h3>일정 관리</h3>
            <p>
              면접 일정을 추가하고 Google 캘린더와 연동하여
              중요한 일정을 놓치지 마세요.
            </p>
          </div>
          <div className={styles.featureCard}>
            <div className={styles.featureIcon}>🔔</div>
            <h3>스마트 알림</h3>
            <p>
              마감 임박, 면접 리마인더, 팔로업 추천까지
              적시에 알림을 받아보세요.
            </p>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className={styles.howItWorks}>
        <div className={styles.sectionHeader}>
          <h2 className={styles.sectionTitle}>시작하기</h2>
          <p className={styles.sectionDescription}>
            단 3단계로 취업 지원 관리를 시작하세요
          </p>
        </div>
        <div className={styles.steps}>
          <div className={styles.step}>
            <div className={styles.stepNumber}>01</div>
            <h3>Google로 로그인</h3>
            <p>간편하게 Google 계정으로 시작하세요. 별도 가입 절차 없이 바로 이용 가능합니다.</p>
          </div>
          <div className={styles.stepConnector}></div>
          <div className={styles.step}>
            <div className={styles.stepNumber}>02</div>
            <h3>목표 설정</h3>
            <p>희망 직무, 경력 레벨, 지역을 설정하면 맞춤 분석을 제공합니다.</p>
          </div>
          <div className={styles.stepConnector}></div>
          <div className={styles.step}>
            <div className={styles.stepNumber}>03</div>
            <h3>지원 추가</h3>
            <p>수동으로 추가하거나 Gmail 연동으로 자동 업데이트하세요.</p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className={styles.cta}>
        <div className={styles.ctaContent}>
          <h2>지금 바로 시작하세요</h2>
          <p>무료로 시작하고, 취업 성공률을 높이세요</p>
          <Link href="/dashboard" className="btn btn-primary btn-lg">
            무료로 시작하기 →
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className={styles.footer}>
        <div className={styles.footerContent}>
          <div className={styles.footerBrand}>
            <div className={styles.logo}>
              <div className={styles.logoIcon}>🚀</div>
              <span>JobPulse</span>
            </div>
            <p>취업 지원을 더 스마트하게</p>
          </div>
          <div className={styles.footerLinks}>
            <div className={styles.footerColumn}>
              <h4>제품</h4>
              <a href="#">기능</a>
              <a href="#">가격</a>
              <a href="#">로드맵</a>
            </div>
            <div className={styles.footerColumn}>
              <h4>리소스</h4>
              <a href="#">가이드</a>
              <a href="#">블로그</a>
              <a href="#">FAQ</a>
            </div>
            <div className={styles.footerColumn}>
              <h4>회사</h4>
              <a href="#">소개</a>
              <a href="#">문의</a>
              <a href="#">채용</a>
            </div>
          </div>
        </div>
        <div className={styles.footerBottom}>
          <p>© 2024 JobPulse. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
