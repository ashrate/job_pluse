# JobPulse 🚀

> 여러 취업 채널의 지원 현황을 통합 관리하고, 기업/공고 정보를 근거 기반으로 요약하며, 이력서를 AI로 진단하는 취업 지원 플랫폼

## 🎯 주요 기능

### 📋 지원현황 통합 관리
- 칸반 보드 기반 파이프라인 (관심 → 지원 → 서류 → 면접 → 오퍼)
- 드래그 앤 드롭으로 상태 변경
- 면접 일정 관리 및 알림
- Gmail/캘린더 연동으로 자동 업데이트

### 🏢 기업/공고 리서치
- RAG 기반 기업 정보 요약
- 출처 기반 신뢰성 있는 정보 제공
- 공고 JD 분석 및 키워드 추출

### 📄 이력서 AI 진단
- ATS 친화도 분석
- 임팩트/성과 표현 개선 제안
- 타겟 공고와의 키워드 매칭
- 버전별 점수 추적

## 🛠 기술 스택

### Frontend
- **Next.js 14** - React 기반 풀스택 프레임워크
- **TypeScript** - 타입 안정성
- **Vanilla CSS** - 커스텀 디자인 시스템

### Backend
- **FastAPI** - Python 고성능 API 프레임워크
- **PostgreSQL** - 관계형 데이터베이스
- **SQLAlchemy** - ORM

### AI/ML
- **OpenAI API** - LLM 기반 분석
- **LangChain** - RAG 파이프라인

## 📁 프로젝트 구조

```
jobpulse/
├── apps/
│   ├── web/                    # Next.js Frontend
│   └── api/                    # FastAPI Backend
├── packages/
│   ├── shared/                 # 공유 타입/유틸
│   └── ai-pipeline/            # AI 분석 파이프라인
├── docker-compose.yml
└── README.md
```

## 🚀 시작하기

### 사전 요구사항
- Node.js 18+
- Python 3.11+
- PostgreSQL 14+

### 프론트엔드 실행
```bash
cd apps/web
npm install
npm run dev
```

### 백엔드 실행
```bash
cd apps/api
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 📝 환경 변수

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend (.env)
```
DATABASE_URL=postgresql://user:password@localhost:5432/jobpulse
SECRET_KEY=your-secret-key
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
OPENAI_API_KEY=your-openai-api-key
```

## 📄 라이센스

MIT License

---

## 🌐 GitHub Pages 배포

### 자동 배포 (GitHub Actions)

1. **GitHub 리포지토리 설정**
   - Settings → Pages → Source를 "GitHub Actions"로 선택

2. **코드 푸시**
   ```bash
   git add .
   git commit -m "Deploy to GitHub Pages"
   git push origin main
   ```

3. **자동 배포 완료**
   - `.github/workflows/deploy-pages.yml` 워크플로우가 자동 실행
   - 배포 URL: `https://<username>.github.io/jobpulse/`

### 수동 빌드 (로컬)

```bash
cd apps/web
npm run build
# 빌드 결과물: out/ 폴더
```

### 주의사항

- GitHub Pages는 **정적 호스팅**만 지원합니다
- 백엔드(API)는 별도 서버가 필요합니다 (Railway, Vercel, AWS 등)
- 프론트엔드는 Mock 데이터로 데모 가능합니다
