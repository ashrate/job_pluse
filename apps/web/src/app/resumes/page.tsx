'use client';

import { useState, useRef, useCallback } from 'react';
import Header from '@/components/layout/Header';
import styles from './page.module.css';

interface Resume {
    id: string;
    filename: string;
    targetRole: string;
    score: number | null;
    hasAnalysis: boolean;
    createdAt: string;
    fileSize?: string;
}

const mockAnalysis = {
    overall_score: 72,
    sections: {
        ats_friendly: { score: 85, status: 'good', feedback: 'ATS 파싱에 적합한 구조입니다.' },
        impact_metrics: { score: 60, status: 'needs_improvement', feedback: '성과를 수치로 더 구체화하세요.' },
        keyword_match: { score: 78, status: 'good', feedback: '주요 키워드가 적절히 포함되어 있습니다.' },
        readability: { score: 65, status: 'needs_improvement', feedback: '문장을 더 간결하게 작성하세요.' },
        format: { score: 72, status: 'good', feedback: '레이아웃이 깔끔합니다.' },
    },
    writingTips: [
        { category: '성과 수치화', tip: '성과에 수치를 추가하세요', example: '"프로젝트 수행" → "매출 20% 증가에 기여한 프로젝트 리드"', reason: '임팩트 수치 추가' },
        { category: '기술 스택 구체화', tip: '기술명을 구체적으로 나열하세요', example: '"다양한 기술" → "Python, React, PostgreSQL, AWS"', reason: '구체적 기술명 나열' },
    ],
};

export default function ResumesPage() {
    const [resumes, setResumes] = useState<Resume[]>([
        { id: '1', filename: '이력서_프론트엔드_2024.pdf', targetRole: 'Frontend Engineer', score: 72, hasAnalysis: true, createdAt: '2024-01-10', fileSize: '245 KB' },
        { id: '2', filename: '이력서_풀스택_2024.pdf', targetRole: 'Full Stack Developer', score: null, hasAnalysis: false, createdAt: '2024-01-05', fileSize: '312 KB' },
    ]);
    const [selectedResume, setSelectedResume] = useState<string | null>(resumes[0]?.id || null);
    const [isUploading, setIsUploading] = useState(false);
    const [uploadState, setUploadState] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle');
    const [uploadProgress, setUploadProgress] = useState(0);
    const [uploadForm, setUploadForm] = useState({
        targetRole: '',
        piiMasking: false,
    });
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [dragActive, setDragActive] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);

    // Analysis states
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [analysisProgress, setAnalysisProgress] = useState(0);
    const [analysisResults, setAnalysisResults] = useState<Record<string, typeof mockAnalysis>>({});

    const selectedResumeData = resumes.find(r => r.id === selectedResume);

    const formatFileSize = (bytes: number): string => {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    };

    const handleDrag = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === 'dragenter' || e.type === 'dragover') {
            setDragActive(true);
        } else if (e.type === 'dragleave') {
            setDragActive(false);
        }
    }, []);

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            const file = e.dataTransfer.files[0];
            if (file.type === 'application/pdf' ||
                file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') {
                setSelectedFile(file);
            } else {
                alert('PDF 또는 DOCX 파일만 업로드 가능합니다.');
            }
        }
    }, []);

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setSelectedFile(e.target.files[0]);
        }
    };

    const handleUpload = async () => {
        if (!selectedFile) {
            alert('파일을 선택해주세요.');
            return;
        }

        if (!uploadForm.targetRole.trim()) {
            alert('타겟 직무를 입력해주세요.');
            return;
        }

        setUploadState('uploading');
        setUploadProgress(0);

        // Simulate upload progress
        const progressInterval = setInterval(() => {
            setUploadProgress(prev => {
                if (prev >= 90) {
                    clearInterval(progressInterval);
                    return prev;
                }
                return prev + 10;
            });
        }, 200);

        try {
            // Simulate API call
            await new Promise(resolve => setTimeout(resolve, 2000));

            clearInterval(progressInterval);
            setUploadProgress(100);

            // Add new resume to list
            const newResume: Resume = {
                id: Date.now().toString(),
                filename: selectedFile.name,
                targetRole: uploadForm.targetRole,
                score: null,
                hasAnalysis: false,
                createdAt: new Date().toISOString().split('T')[0],
                fileSize: formatFileSize(selectedFile.size),
            };

            setResumes(prev => [newResume, ...prev]);
            setSelectedResume(newResume.id);
            setUploadState('success');

            // Reset and close modal after short delay
            setTimeout(() => {
                setIsUploading(false);
                setUploadState('idle');
                setUploadProgress(0);
                setSelectedFile(null);
                setUploadForm({ targetRole: '', piiMasking: false });
            }, 1500);

        } catch (error) {
            clearInterval(progressInterval);
            setUploadState('error');
            console.error('Upload error:', error);
        }
    };

    const handleDeleteResume = (id: string) => {
        if (confirm('이 이력서를 삭제하시겠습니까?')) {
            setResumes(prev => prev.filter(r => r.id !== id));
            if (selectedResume === id) {
                setSelectedResume(resumes.find(r => r.id !== id)?.id || null);
            }
        }
    };

    const closeModal = () => {
        if (uploadState === 'uploading') return;
        setIsUploading(false);
        setUploadState('idle');
        setUploadProgress(0);
        setSelectedFile(null);
        setUploadForm({ targetRole: '', piiMasking: false });
    };

    // Generate analysis based on resume info (filename, target role)
    const generateAnalysisResult = (resume: Resume) => {
        const filename = resume.filename.toLowerCase();
        const targetRole = resume.targetRole.toLowerCase();

        // Detect resume type from filename and target role
        const isFrontend = filename.includes('프론트') || filename.includes('front') ||
            targetRole.includes('프론트') || targetRole.includes('front') || targetRole.includes('react');
        const isBackend = filename.includes('백엔드') || filename.includes('back') ||
            targetRole.includes('백엔드') || targetRole.includes('back') || targetRole.includes('서버');
        const isFullstack = filename.includes('풀스택') || filename.includes('full') ||
            targetRole.includes('풀스택') || targetRole.includes('full');
        const isData = filename.includes('데이터') || filename.includes('data') ||
            targetRole.includes('데이터') || targetRole.includes('data') || targetRole.includes('분석');
        const isDevOps = targetRole.includes('devops') || targetRole.includes('운영') || targetRole.includes('인프라');

        // Generate role-specific writing tips (not based on actual resume content)
        const getWritingTips = () => {
            if (isFrontend) {
                return [
                    {
                        category: '기술 스택 작성법',
                        tip: 'React, TypeScript, Next.js 등 구체적인 기술명을 나열하세요',
                        example: '"웹 개발 경험" → "React, TypeScript, Next.js를 활용한 SPA 개발 3년 경력"',
                        reason: `${resume.targetRole} 직무에서 기술 스택 명시는 필수입니다`
                    },
                    {
                        category: '성과 수치화',
                        tip: '성능 개선, 사용자 지표 등을 수치로 표현하세요',
                        example: '"UI 개선" → "Core Web Vitals LCP 2.5s→1.2s 개선, 이탈률 25% 감소"',
                        reason: '수치가 있으면 임팩트가 명확해집니다'
                    },
                    {
                        category: '프로젝트 규모',
                        tip: 'DAU, MAU, 트래픽 등 서비스 규모를 명시하세요',
                        example: '"웹 서비스 개발" → "월 10만 DAU 서비스의 프론트엔드 설계 및 개발"',
                        reason: '규모를 언급하면 경험의 깊이를 보여줄 수 있습니다'
                    }
                ];
            } else if (isBackend) {
                return [
                    {
                        category: '기술 스택 작성법',
                        tip: '언어, 프레임워크, DB, 인프라를 구체적으로 나열하세요',
                        example: '"서버 개발" → "Node.js, PostgreSQL, Redis, Docker 기반 백엔드 시스템 구축"',
                        reason: `${resume.targetRole} 직무에서 기술 스택 명시는 필수입니다`
                    },
                    {
                        category: '성능 개선 성과',
                        tip: 'API 응답시간, 처리량 등 성능 지표를 수치로 표현하세요',
                        example: '"API 개발" → "API 응답시간 200ms→50ms 개선 (75% 향상)"',
                        reason: '백엔드는 성능 수치가 핵심 역량 지표입니다'
                    },
                    {
                        category: '트래픽/데이터 규모',
                        tip: '처리한 데이터나 트래픽 규모를 언급하세요',
                        example: '"DB 관리" → "일 1억건 트래픽을 처리하는 DB 쿼리 최적화"',
                        reason: '규모를 언급하면 대용량 시스템 경험을 증명할 수 있습니다'
                    }
                ];
            } else if (isFullstack) {
                return [
                    {
                        category: '풀스택 역량 표현',
                        tip: '프론트엔드, 백엔드 기술을 모두 명시하세요',
                        example: '"웹 개발" → "React + Node.js + PostgreSQL 기반 풀스택 서비스 개발"',
                        reason: '풀스택은 양쪽 기술 스택을 모두 보여줘야 합니다'
                    },
                    {
                        category: '종합적 성과',
                        tip: '서비스 전체를 담당한 경험을 강조하세요',
                        example: '"서비스 개발" → "0→1 서비스 구축부터 MAU 5만 달성까지 전 과정 주도"',
                        reason: '풀스택의 가치는 전체를 볼 수 있다는 점입니다'
                    },
                    {
                        category: '1인 개발 역량',
                        tip: '독립적으로 완수한 프로젝트를 강조하세요',
                        example: '"개발 담당" → "FE/BE/인프라를 아우르는 1인 개발로 MVP 2주 내 출시"',
                        reason: '자기주도적 개발 능력을 보여줄 수 있습니다'
                    }
                ];
            } else if (isData) {
                return [
                    {
                        category: '분석 도구 명시',
                        tip: '사용한 분석 도구와 언어를 구체적으로 나열하세요',
                        example: '"데이터 분석" → "Python, SQL, Pandas, Scikit-learn으로 ML 모델 개발"',
                        reason: '데이터 직무는 도구 숙련도가 중요합니다'
                    },
                    {
                        category: '비즈니스 임팩트',
                        tip: '분석 결과가 비즈니스에 미친 영향을 수치로 표현하세요',
                        example: '"분석 업무" → "이탈 예측 모델로 마케팅 비용 30% 절감에 기여"',
                        reason: '분석의 가치는 비즈니스 성과로 증명됩니다'
                    },
                    {
                        category: '데이터 규모',
                        tip: '처리한 데이터의 규모를 언급하세요',
                        example: '"ETL 구축" → "일 500GB 데이터 처리하는 파이프라인 설계 및 자동화"',
                        reason: '대용량 데이터 처리 경험을 보여줄 수 있습니다'
                    }
                ];
            } else {
                return [
                    {
                        category: '성과 수치화',
                        tip: '모든 성과에 수치를 붙여보세요',
                        example: '"프로젝트 수행" → "사용자 수 50% 증가에 기여한 핵심 기능 개발 리드"',
                        reason: '수치가 없는 성과는 임팩트가 약해 보입니다'
                    },
                    {
                        category: '기술 스택 구체화',
                        tip: `${resume.targetRole}에 필요한 핵심 기술을 구체적으로 나열하세요`,
                        example: '"다양한 기술 활용" → "Python, SQL, Excel VBA 등 업무 자동화 도구 활용"',
                        reason: '구체적인 기술명이 키워드 매칭에 유리합니다'
                    },
                    {
                        category: '경험 구체화',
                        tip: '추상적인 표현 대신 구체적인 경험을 작성하세요',
                        example: '"열정적으로 일함" → "3년간 스타트업에서 0→1 제품 개발 3회 완수"',
                        reason: '구체적인 경험이 신뢰도를 높입니다'
                    }
                ];
            }
        };

        // Generate role-specific feedback
        const getRoleKeywords = () => {
            if (isFrontend) return ['React', 'TypeScript', 'Next.js', 'CSS', 'JavaScript', 'HTML'];
            if (isBackend) return ['Node.js', 'Python', 'SQL', 'API', 'Docker', 'AWS'];
            if (isFullstack) return ['React', 'Node.js', 'TypeScript', 'PostgreSQL', 'Docker'];
            if (isData) return ['Python', 'SQL', 'Pandas', 'ML', '데이터분석', 'Tableau'];
            if (isDevOps) return ['Docker', 'Kubernetes', 'AWS', 'CI/CD', 'Terraform', 'Linux'];
            return ['협업', '문제해결', '커뮤니케이션', '기획', '분석'];
        };

        const baseScore = 62 + Math.floor(Math.random() * 20);
        const keywords = getRoleKeywords();

        return {
            overall_score: baseScore,
            sections: {
                ats_friendly: {
                    score: Math.min(100, baseScore + 8 + Math.floor(Math.random() * 10)),
                    status: 'good' as const,
                    feedback: 'PDF 형식의 이력서로 ATS 시스템에서 파싱이 잘 됩니다. 표준화된 섹션 구분을 사용하세요.'
                },
                impact_metrics: {
                    score: Math.min(100, baseScore - 5 + Math.floor(Math.random() * 15)),
                    status: baseScore > 70 ? 'good' : 'needs_improvement',
                    feedback: baseScore > 70
                        ? '성과가 수치와 함께 잘 표현되어 있습니다. 더 구체적인 비즈니스 임팩트를 추가하면 좋습니다.'
                        : '성과를 수치로 표현하세요. "매출 증가"보다 "매출 30% 증가"가 훨씬 임팩트 있습니다.'
                },
                keyword_match: {
                    score: Math.min(100, baseScore + 5 + Math.floor(Math.random() * 12)),
                    status: 'good' as const,
                    feedback: `${resume.targetRole} 직무와 관련된 핵심 키워드(${keywords.slice(0, 3).join(', ')})가 포함되어 있습니다. ${keywords.slice(3, 5).join(', ')} 키워드 추가를 권장합니다.`
                },
                readability: {
                    score: Math.min(100, baseScore + Math.floor(Math.random() * 15)),
                    status: baseScore > 65 ? 'good' : 'needs_improvement',
                    feedback: baseScore > 65
                        ? '문장이 간결하고 읽기 쉽게 작성되어 있습니다.'
                        : '문장을 더 간결하게 작성하세요. 한 문장에 핵심 정보 하나만 담는 것이 좋습니다.'
                },
                format: {
                    score: Math.min(100, baseScore + 10 + Math.floor(Math.random() * 8)),
                    status: 'good' as const,
                    feedback: '레이아웃이 깔끔하게 정돈되어 있습니다. 글머리 기호를 활용하면 가독성이 더 높아집니다.'
                },
            },
            writingTips: getWritingTips(),
        };
    };

    const handleStartAnalysis = async (resumeId: string) => {
        setIsAnalyzing(true);
        setAnalysisProgress(0);

        // Simulate analysis progress
        const progressInterval = setInterval(() => {
            setAnalysisProgress(prev => {
                if (prev >= 95) {
                    clearInterval(progressInterval);
                    return prev;
                }
                return prev + Math.floor(Math.random() * 8) + 3;
            });
        }, 400);

        try {
            // Simulate API call for analysis (3-5 seconds)
            await new Promise(resolve => setTimeout(resolve, 3500));

            clearInterval(progressInterval);
            setAnalysisProgress(100);

            // Find the resume being analyzed
            const targetResume = resumes.find(r => r.id === resumeId);
            if (!targetResume) {
                throw new Error('Resume not found');
            }

            // Generate analysis result based on resume info
            const result = generateAnalysisResult(targetResume);

            // Store result
            setAnalysisResults(prev => ({
                ...prev,
                [resumeId]: result
            }));

            // Update resume to show it has analysis
            setResumes(prev => prev.map(r =>
                r.id === resumeId
                    ? { ...r, hasAnalysis: true, score: result.overall_score }
                    : r
            ));

            // Short delay before hiding progress
            await new Promise(resolve => setTimeout(resolve, 500));

        } catch (error) {
            console.error('Analysis error:', error);
            clearInterval(progressInterval);
        } finally {
            setIsAnalyzing(false);
            setAnalysisProgress(0);
        }
    };

    // Get analysis for current resume (either stored or mock)
    const getCurrentAnalysis = () => {
        if (!selectedResume) return mockAnalysis;
        return analysisResults[selectedResume] || mockAnalysis;
    };


    return (
        <>
            <Header
                title="이력서"
                subtitle="이력서를 업로드하고 AI 진단을 받아보세요"
                actions={
                    <button
                        className="btn btn-primary"
                        onClick={() => setIsUploading(true)}
                    >
                        + 이력서 업로드
                    </button>
                }
            />

            <div className={styles.content}>
                <div className={styles.grid}>
                    {/* Resume List */}
                    <div className={styles.listSection}>
                        <h2 className={styles.sectionTitle}>내 이력서 ({resumes.length})</h2>
                        <div className={styles.resumeList}>
                            {resumes.map((resume) => (
                                <div
                                    key={resume.id}
                                    className={`${styles.resumeCard} ${selectedResume === resume.id ? styles.selected : ''}`}
                                    onClick={() => setSelectedResume(resume.id)}
                                >
                                    <div className={styles.resumeIcon}>📄</div>
                                    <div className={styles.resumeInfo}>
                                        <div className={styles.resumeName}>{resume.filename}</div>
                                        <div className={styles.resumeMeta}>
                                            <span>{resume.targetRole}</span>
                                            <span>•</span>
                                            <span>{resume.createdAt}</span>
                                            {resume.fileSize && (
                                                <>
                                                    <span>•</span>
                                                    <span>{resume.fileSize}</span>
                                                </>
                                            )}
                                        </div>
                                    </div>
                                    {resume.score !== null && (
                                        <div className={styles.resumeScore}>
                                            <span className={styles.scoreValue}>{resume.score}</span>
                                            <span className={styles.scoreLabel}>점</span>
                                        </div>
                                    )}
                                    {resume.score === null && !resume.hasAnalysis && (
                                        <span className={`badge ${styles.pendingBadge}`}>분석 필요</span>
                                    )}
                                    <button
                                        className={styles.deleteBtn}
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            handleDeleteResume(resume.id);
                                        }}
                                        title="삭제"
                                    >
                                        🗑️
                                    </button>
                                </div>
                            ))}

                            {resumes.length === 0 && (
                                <div className={styles.emptyState}>
                                    <span className={styles.emptyIcon}>📭</span>
                                    <p>아직 업로드한 이력서가 없습니다</p>
                                    <button
                                        className="btn btn-primary"
                                        onClick={() => setIsUploading(true)}
                                    >
                                        첫 이력서 업로드
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Analysis Report */}
                    <div className={styles.reportSection}>
                        {selectedResumeData?.hasAnalysis ? (
                            <>
                                <h2 className={styles.sectionTitle}>📊 AI 진단 리포트</h2>

                                {/* Overall Score */}
                                <div className={styles.scoreCard}>
                                    <div className={styles.scoreCircle} style={{ '--progress': `${getCurrentAnalysis().overall_score}%` } as React.CSSProperties}>
                                        <div className={styles.scoreCircleInner}>
                                            <span className={styles.scoreCircleValue}>{getCurrentAnalysis().overall_score}</span>
                                            <span className={styles.scoreCircleLabel}>/ 100</span>
                                        </div>
                                    </div>
                                    <div className={styles.scoreDesc}>
                                        <h3>종합 점수</h3>
                                        <p>
                                            {getCurrentAnalysis().overall_score >= 80 ? '우수한 이력서입니다! 세부 사항만 다듬으면 완벽합니다.' :
                                                getCurrentAnalysis().overall_score >= 65 ? '양호한 이력서입니다. 몇 가지 개선점을 반영하면 더 좋아질 수 있습니다.' :
                                                    '개선이 필요한 이력서입니다. 아래 제안사항을 참고해주세요.'}
                                        </p>
                                    </div>
                                </div>

                                {/* Section Scores */}
                                <div className={styles.sectionsGrid}>
                                    {Object.entries(getCurrentAnalysis().sections).map(([key, section]) => (
                                        <div key={key} className={styles.sectionCard}>
                                            <div className={styles.sectionHeader}>
                                                <span className={styles.sectionIcon}>
                                                    {section.status === 'good' ? '✅' : '⚠️'}
                                                </span>
                                                <span className={styles.sectionName}>
                                                    {key === 'ats_friendly' && 'ATS 친화도'}
                                                    {key === 'impact_metrics' && '임팩트'}
                                                    {key === 'keyword_match' && '키워드 매칭'}
                                                    {key === 'readability' && '가독성'}
                                                    {key === 'format' && '형식'}
                                                </span>
                                                <span className={styles.sectionScore}>{section.score}점</span>
                                            </div>
                                            <div className={styles.sectionProgress}>
                                                <div
                                                    className={`${styles.sectionProgressBar} ${section.status === 'good' ? styles.good : styles.warning}`}
                                                    style={{ width: `${section.score}%` }}
                                                ></div>
                                            </div>
                                            <p className={styles.sectionFeedback}>{section.feedback}</p>
                                        </div>
                                    ))}
                                </div>

                                {/* Writing Tips - 직무 맞춤 작성 가이드 */}
                                <div className={styles.suggestionsSection}>
                                    <h3 className={styles.suggestionsTitle}>📝 {selectedResumeData?.targetRole} 이력서 작성 가이드</h3>
                                    <p className={styles.guideNotice}>* 아래는 해당 직무에 맞는 일반적인 작성 팁입니다</p>
                                    {getCurrentAnalysis().writingTips.map((tip: { category: string; tip: string; example: string; reason: string }, index: number) => (
                                        <div key={index} className={styles.tipCard}>
                                            <div className={styles.tipHeader}>
                                                <span className={styles.tipCategory}>📌 {tip.category}</span>
                                            </div>
                                            <div className={styles.tipContent}>
                                                <div className={styles.tipMain}>
                                                    <span className={styles.tipLabel}>💡 팁</span>
                                                    <span className={styles.tipText}>{tip.tip}</span>
                                                </div>
                                                <div className={styles.tipExample}>
                                                    <span className={styles.tipLabel}>✏️ 예시</span>
                                                    <span className={styles.tipExampleText}>{tip.example}</span>
                                                </div>
                                                <div className={styles.tipReason}>
                                                    <span className={styles.tipReasonText}>→ {tip.reason}</span>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </>
                        ) : selectedResumeData ? (
                            <div className={styles.analyzePrompt}>
                                {isAnalyzing ? (
                                    <>
                                        <div className={styles.analyzingSpinner}></div>
                                        <h3>AI 분석 중...</h3>
                                        <div className={styles.analysisProgressBar}>
                                            <div
                                                className={styles.analysisProgressFill}
                                                style={{ width: `${analysisProgress}%` }}
                                            ></div>
                                        </div>
                                        <p className={styles.analysisStep}>
                                            {analysisProgress < 20 && '📄 이력서 파싱 중...'}
                                            {analysisProgress >= 20 && analysisProgress < 40 && '🔍 ATS 호환성 검사 중...'}
                                            {analysisProgress >= 40 && analysisProgress < 60 && '📊 임팩트 분석 중...'}
                                            {analysisProgress >= 60 && analysisProgress < 80 && '🔑 키워드 매칭 분석 중...'}
                                            {analysisProgress >= 80 && '✨ 개선 제안 생성 중...'}
                                        </p>
                                    </>
                                ) : (
                                    <>
                                        <div className={styles.promptIcon}>🔍</div>
                                        <h3>AI 분석 실행</h3>
                                        <p>이 이력서에 대한 AI 진단을 받아보세요. ATS 친화도, 임팩트 표현, 키워드 매칭 등을 분석합니다.</p>
                                        <button
                                            className="btn btn-primary btn-lg"
                                            onClick={() => handleStartAnalysis(selectedResumeData.id)}
                                        >
                                            🤖 AI 분석 시작
                                        </button>
                                    </>
                                )}
                            </div>
                        ) : (
                            <div className={styles.emptyReport}>
                                <span className={styles.emptyIcon}>📋</span>
                                <p>이력서를 선택하면 분석 리포트를 볼 수 있습니다</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Upload Modal */}
            {isUploading && (
                <div className={styles.modalOverlay} onClick={closeModal}>
                    <div className={styles.modal} onClick={e => e.stopPropagation()}>
                        <div className={styles.modalHeader}>
                            <h2>이력서 업로드</h2>
                            <button className={styles.closeBtn} onClick={closeModal}>✕</button>
                        </div>
                        <div className={styles.modalBody}>
                            {uploadState === 'success' ? (
                                <div className={styles.uploadSuccess}>
                                    <span className={styles.successIcon}>✅</span>
                                    <h3>업로드 완료!</h3>
                                    <p>이력서가 성공적으로 업로드되었습니다.</p>
                                </div>
                            ) : (
                                <>
                                    <div
                                        className={`${styles.uploadArea} ${dragActive ? styles.dragActive : ''} ${selectedFile ? styles.hasFile : ''}`}
                                        onDragEnter={handleDrag}
                                        onDragLeave={handleDrag}
                                        onDragOver={handleDrag}
                                        onDrop={handleDrop}
                                        onClick={() => fileInputRef.current?.click()}
                                    >
                                        {selectedFile ? (
                                            <div className={styles.selectedFile}>
                                                <span className={styles.fileIcon}>📄</span>
                                                <div className={styles.fileInfo}>
                                                    <span className={styles.fileName}>{selectedFile.name}</span>
                                                    <span className={styles.fileSize}>{formatFileSize(selectedFile.size)}</span>
                                                </div>
                                                <button
                                                    className={styles.removeFile}
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        setSelectedFile(null);
                                                    }}
                                                >
                                                    ✕
                                                </button>
                                            </div>
                                        ) : (
                                            <>
                                                <span className={styles.uploadIcon}>📤</span>
                                                <p>PDF 또는 DOCX 파일을 드래그하거나 클릭하여 업로드</p>
                                                <span className={styles.uploadHint}>최대 10MB</span>
                                            </>
                                        )}
                                        <input
                                            ref={fileInputRef}
                                            type="file"
                                            accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                                            className={styles.fileInput}
                                            onChange={handleFileSelect}
                                        />
                                    </div>

                                    {uploadState === 'uploading' && (
                                        <div className={styles.progressBar}>
                                            <div
                                                className={styles.progressFill}
                                                style={{ width: `${uploadProgress}%` }}
                                            ></div>
                                            <span className={styles.progressText}>{uploadProgress}%</span>
                                        </div>
                                    )}

                                    <div className={styles.formGroup}>
                                        <label className={styles.label}>타겟 직무 *</label>
                                        <input
                                            type="text"
                                            className="input"
                                            placeholder="예: Frontend Engineer"
                                            value={uploadForm.targetRole}
                                            onChange={e => setUploadForm(prev => ({ ...prev, targetRole: e.target.value }))}
                                            disabled={uploadState === 'uploading'}
                                        />
                                    </div>

                                    <div className={styles.formGroup}>
                                        <label className={styles.checkbox}>
                                            <input
                                                type="checkbox"
                                                checked={uploadForm.piiMasking}
                                                onChange={e => setUploadForm(prev => ({ ...prev, piiMasking: e.target.checked }))}
                                                disabled={uploadState === 'uploading'}
                                            />
                                            <span>PII 마스킹 (개인정보 마스킹)</span>
                                        </label>
                                        <p className={styles.checkboxHint}>
                                            이름, 전화번호, 이메일 등 개인정보를 마스킹하여 분석합니다.
                                        </p>
                                    </div>
                                </>
                            )}
                        </div>
                        {uploadState !== 'success' && (
                            <div className={styles.modalFooter}>
                                <button
                                    className="btn btn-secondary"
                                    onClick={closeModal}
                                    disabled={uploadState === 'uploading'}
                                >
                                    취소
                                </button>
                                <button
                                    className="btn btn-primary"
                                    onClick={handleUpload}
                                    disabled={uploadState === 'uploading' || !selectedFile}
                                >
                                    {uploadState === 'uploading' ? '업로드 중...' : '업로드'}
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </>
    );
}
