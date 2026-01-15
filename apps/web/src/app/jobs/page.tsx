'use client';

import { useState, useMemo } from 'react';
import Header from '@/components/layout/Header';
import styles from './page.module.css';

interface Job {
    title: string;
    company_name: string;
    source: string;
    source_url: string;
    source_id: string;
    location: string | null;
    experience_level: string | null;
    employment_type: string | null;
    skills: string[];
    company_logo_url: string | null;
    crawled_at: string;
    description?: string | null;
    requirements?: string | null;
    benefits?: string | null;
    salary?: string | null;
    deadline?: string | null;
    posted_at?: string | null;
}

interface SearchState {
    keyword: string;
    location: string;
    experience: string;
    sources: string[];
    hideExpired: boolean;
}

const SOURCES = [
    { id: 'wanted', name: '원티드', icon: '💜', color: '#3366FF' },
    { id: 'jobkorea', name: '잡코리아', icon: '🔵', color: '#1E90FF' },
    { id: 'jobplanet', name: '잡플래닛', icon: '🌍', color: '#00C853' },
    { id: 'linkedin', name: '링크드인', icon: '🔗', color: '#0077B5' },
];

const LOCATIONS = ['전체', '서울', '경기', '인천', '부산', '대구', '대전', '광주'];
const EXPERIENCE_LEVELS = ['전체', '신입', '경력', '신입/경력'];

// Mock data for UI demonstration - source_url은 실제 플랫폼 채용 검색 페이지로 연결
const mockJobs: Job[] = [
    {
        title: 'Frontend Engineer',
        company_name: '네이버',
        source: 'wanted',
        source_url: 'https://www.wanted.co.kr/search?query=프론트엔드&tab=position',
        source_id: '12345',
        location: '서울 강남구',
        experience_level: '3~5년',
        employment_type: '정규직',
        skills: ['React', 'TypeScript', 'Next.js', 'GraphQL', 'Jest'],
        company_logo_url: null,
        crawled_at: new Date().toISOString(),
        description: '네이버 서비스의 프론트엔드 개발을 담당합니다. React 기반의 대규모 웹 애플리케이션을 개발하고 유지보수합니다. 사용자 경험 개선을 위한 성능 최적화 작업을 수행합니다.',
        requirements: '• React/Vue.js 개발 경력 3년 이상\n• TypeScript 사용 경험\n• 대규모 트래픽 서비스 경험\n• 웹 표준 및 접근성에 대한 이해',
        benefits: '• 자율 출퇴근\n• 원격 근무 가능\n• 연봉 협상 가능\n• 스톡옵션 지급',
        salary: '6,000만원 ~ 8,000만원',
        deadline: '2026-02-15',
        posted_at: '2026-01-10',
    },
    {
        title: 'React Developer',
        company_name: '카카오',
        source: 'jobkorea',
        source_url: 'https://www.jobkorea.co.kr/Search/?stext=React',
        source_id: '123',
        location: '경기 성남시',
        experience_level: '1~3년',
        employment_type: '정규직',
        skills: ['React', 'JavaScript', 'Redux', 'Webpack'],
        company_logo_url: null,
        crawled_at: new Date().toISOString(),
        description: '카카오톡 웹 버전의 프론트엔드를 개발합니다. 대규모 사용자를 위한 최적화된 UI/UX를 구현합니다.',
        requirements: '• React 개발 경력 1년 이상\n• JavaScript/ES6+ 능숙\n• 상태 관리 라이브러리 사용 경험',
        benefits: '• 유연 근무제\n• 자기계발 지원금\n• 건강검진 지원',
        salary: '4,500만원 ~ 6,000만원',
        deadline: '2026-02-28',
        posted_at: '2026-01-08',
    },
    {
        title: 'Senior Frontend Developer',
        company_name: '토스',
        source: 'linkedin',
        source_url: 'https://www.linkedin.com/jobs/search/?keywords=Frontend%20Developer&location=South%20Korea',
        source_id: '123',
        location: '서울 강남구',
        experience_level: '5년 이상',
        employment_type: '정규직',
        skills: ['React', 'TypeScript', 'GraphQL', 'Testing', 'CI/CD'],
        company_logo_url: null,
        crawled_at: new Date().toISOString(),
        description: '토스 금융 서비스의 웹 프론트엔드를 리드합니다. 팀원들을 멘토링하고 기술적 의사결정을 주도합니다.',
        requirements: '• 프론트엔드 개발 경력 5년 이상\n• 금융/핀테크 도메인 경험 우대\n• 팀 리딩 경험',
        benefits: '• 스톡옵션\n• 연봉 상위권\n• 원격 근무',
        salary: '8,000만원 ~ 1억원',
        deadline: '2026-01-20',
        posted_at: '2026-01-05',
    },
    {
        title: 'Web Frontend Engineer',
        company_name: '쿠팡',
        source: 'jobplanet',
        source_url: 'https://www.jobplanet.co.kr/search?query=프론트엔드',
        source_id: '123',
        location: '서울 송파구',
        experience_level: '3~5년',
        employment_type: '정규직',
        skills: ['Vue.js', 'JavaScript', 'CSS', 'Nuxt.js'],
        company_logo_url: null,
        crawled_at: new Date().toISOString(),
        description: '쿠팡 이커머스 플랫폼의 웹 프론트엔드를 개발합니다. 수백만 사용자가 이용하는 서비스를 만듭니다.',
        requirements: '• Vue.js 개발 경력 3년 이상\n• 이커머스 경험 우대\n• 성능 최적화 경험',
        benefits: '• 로켓배송 직원 할인\n• 건강검진\n• 학습 지원',
        salary: '협의',
        deadline: '2026-01-10', // 마감된 공고
        posted_at: '2025-12-20',
    },
    {
        title: 'Frontend Developer (신입)',
        company_name: '배달의민족',
        source: 'wanted',
        source_url: 'https://www.wanted.co.kr/search?query=배달의민족&tab=position',
        source_id: '67890',
        location: '서울 송파구',
        experience_level: '신입',
        employment_type: '정규직',
        skills: ['React', 'JavaScript', 'HTML', 'CSS'],
        company_logo_url: null,
        crawled_at: new Date().toISOString(),
        description: '배민 서비스의 프론트엔드 개발에 참여합니다. 신입 개발자를 위한 체계적인 온보딩을 제공합니다.',
        requirements: '• 컴퓨터공학 또는 관련 전공\n• React 학습 경험\n• 포트폴리오 보유자',
        benefits: '• 교육 프로그램\n• 배민 음식 쿠폰\n• 재택 근무',
        salary: '신입 연봉 테이블',
        deadline: '2026-03-01',
        posted_at: '2026-01-12',
    },
];

export default function JobsPage() {
    const [search, setSearch] = useState<SearchState>({
        keyword: '',
        location: '전체',
        experience: '전체',
        sources: ['wanted', 'jobkorea', 'jobplanet', 'linkedin'],
        hideExpired: true,
    });

    const [allJobs] = useState<Job[]>(mockJobs);
    const [loading, setLoading] = useState(false);
    const [searched, setSearched] = useState(false);
    const [selectedJob, setSelectedJob] = useState<Job | null>(null);

    // Filter jobs based on search criteria and deadline
    const filteredJobs = useMemo(() => {
        let jobs = allJobs;

        // Filter by selected sources (platforms)
        if (search.sources.length > 0 && search.sources.length < SOURCES.length) {
            jobs = jobs.filter(job => search.sources.includes(job.source));
        }

        // Filter by search keyword
        if (search.keyword.trim()) {
            const kw = search.keyword.toLowerCase();
            jobs = jobs.filter(job =>
                job.title.toLowerCase().includes(kw) ||
                job.company_name.toLowerCase().includes(kw) ||
                job.skills.some(s => s.toLowerCase().includes(kw))
            );
        }

        // Filter by location
        if (search.location !== '전체') {
            jobs = jobs.filter(job =>
                job.location && job.location.includes(search.location)
            );
        }

        // Filter by experience level
        if (search.experience !== '전체') {
            jobs = jobs.filter(job => {
                if (!job.experience_level) return false;
                if (search.experience === '신입') {
                    return job.experience_level.includes('신입') || job.experience_level === '신입';
                }
                if (search.experience === '경력') {
                    return !job.experience_level.includes('신입');
                }
                if (search.experience === '신입/경력') {
                    return job.experience_level.includes('신입') || job.experience_level.includes('경력');
                }
                return true;
            });
        }

        // Filter expired jobs
        if (search.hideExpired) {
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            jobs = jobs.filter(job => {
                if (!job.deadline) return true;
                const deadline = new Date(job.deadline);
                return deadline >= today;
            });
        }

        return jobs;
    }, [allJobs, search.sources, search.keyword, search.location, search.experience, search.hideExpired]);

    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!search.keyword.trim()) {
            alert('검색어를 입력해주세요');
            return;
        }

        setLoading(true);
        setSearched(true);

        try {
            // Simulate API call
            await new Promise(resolve => setTimeout(resolve, 1000));
        } catch (error) {
            console.error('Search error:', error);
        } finally {
            setLoading(false);
        }
    };

    const toggleSource = (sourceId: string) => {
        setSearch(prev => ({
            ...prev,
            sources: prev.sources.includes(sourceId)
                ? prev.sources.filter(s => s !== sourceId)
                : [...prev.sources, sourceId]
        }));
    };

    const getSourceInfo = (sourceId: string) => {
        return SOURCES.find(s => s.id === sourceId) || { name: sourceId, icon: '📋', color: '#666' };
    };

    const handleApply = (job: Job) => {
        console.log('Apply to:', job);
        alert(`"${job.title}" at ${job.company_name} 지원 추가됨!`);
        setSelectedJob(null);
    };

    const formatDate = (dateStr: string | null | undefined): string => {
        if (!dateStr) return '-';
        const date = new Date(dateStr);
        return date.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric' });
    };

    const isExpiringSoon = (deadline: string | null | undefined): boolean => {
        if (!deadline) return false;
        const deadlineDate = new Date(deadline);
        const today = new Date();
        const diff = deadlineDate.getTime() - today.getTime();
        const daysLeft = diff / (1000 * 60 * 60 * 24);
        return daysLeft <= 7 && daysLeft > 0;
    };

    return (
        <>
            <Header
                title="공고 검색"
                subtitle="잡코리아, 원티드, 잡플래닛, 링크드인에서 채용공고를 검색하세요"
            />

            <div className={styles.content}>
                {/* Search Form */}
                <form className={styles.searchForm} onSubmit={handleSearch}>
                    <div className={styles.searchMain}>
                        <div className={styles.searchInputWrapper}>
                            <span className={styles.searchIcon}>🔍</span>
                            <input
                                type="text"
                                className={styles.searchInput}
                                placeholder="직무, 기술, 회사명으로 검색 (예: 프론트엔드, React, 네이버)"
                                value={search.keyword}
                                onChange={e => setSearch({ ...search, keyword: e.target.value })}
                            />
                        </div>
                        <button type="submit" className={`btn btn-primary ${styles.searchBtn}`} disabled={loading}>
                            {loading ? '검색중...' : '검색'}
                        </button>
                    </div>

                    <div className={styles.filters}>
                        {/* Location Filter */}
                        <div className={styles.filterGroup}>
                            <label className={styles.filterLabel}>지역</label>
                            <select
                                className={styles.filterSelect}
                                value={search.location}
                                onChange={e => setSearch({ ...search, location: e.target.value })}
                            >
                                {LOCATIONS.map(loc => (
                                    <option key={loc} value={loc}>{loc}</option>
                                ))}
                            </select>
                        </div>

                        {/* Experience Filter */}
                        <div className={styles.filterGroup}>
                            <label className={styles.filterLabel}>경력</label>
                            <select
                                className={styles.filterSelect}
                                value={search.experience}
                                onChange={e => setSearch({ ...search, experience: e.target.value })}
                            >
                                {EXPERIENCE_LEVELS.map(exp => (
                                    <option key={exp} value={exp}>{exp}</option>
                                ))}
                            </select>
                        </div>

                        {/* Source Filter */}
                        <div className={styles.filterGroup}>
                            <label className={styles.filterLabel}>플랫폼</label>
                            <div className={styles.sourceToggles}>
                                {SOURCES.map(source => (
                                    <button
                                        key={source.id}
                                        type="button"
                                        className={`${styles.sourceToggle} ${search.sources.includes(source.id) ? styles.active : ''}`}
                                        onClick={() => toggleSource(source.id)}
                                        style={{ '--source-color': source.color } as React.CSSProperties}
                                    >
                                        <span>{source.icon}</span>
                                        <span>{source.name}</span>
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Hide Expired Toggle */}
                        <div className={styles.filterGroup}>
                            <label className={styles.filterLabel}>옵션</label>
                            <label className={styles.toggleLabel}>
                                <input
                                    type="checkbox"
                                    checked={search.hideExpired}
                                    onChange={e => setSearch({ ...search, hideExpired: e.target.checked })}
                                />
                                <span>마감된 공고 숨기기</span>
                            </label>
                        </div>
                    </div>
                </form>

                {/* Results */}
                <div className={styles.results}>
                    {loading ? (
                        <div className={styles.loadingState}>
                            <div className={styles.spinner}></div>
                            <p>채용공고를 검색중입니다...</p>
                            <p className={styles.loadingHint}>잡코리아, 원티드, 잡플래닛, 링크드인에서 검색중</p>
                        </div>
                    ) : searched && filteredJobs.length === 0 ? (
                        <div className={styles.emptyState}>
                            <span className={styles.emptyIcon}>🔍</span>
                            <h3>검색 결과가 없습니다</h3>
                            <p>다른 키워드로 검색하거나, 마감된 공고 숨기기를 해제해보세요</p>
                        </div>
                    ) : (
                        <>
                            {searched && (
                                <div className={styles.resultsHeader}>
                                    <h2>검색 결과 ({filteredJobs.length}건)</h2>
                                </div>
                            )}

                            <div className={styles.jobList}>
                                {filteredJobs.map((job, index) => {
                                    const source = getSourceInfo(job.source);
                                    const expiringSoon = isExpiringSoon(job.deadline);
                                    return (
                                        <div
                                            key={`${job.source}-${job.source_id}-${index}`}
                                            className={styles.jobCard}
                                            onClick={() => setSelectedJob(job)}
                                        >
                                            <div className={styles.jobHeader}>
                                                <div className={styles.companyLogo}>
                                                    {job.company_logo_url ? (
                                                        <img src={job.company_logo_url} alt={job.company_name} />
                                                    ) : (
                                                        <span>{job.company_name[0]}</span>
                                                    )}
                                                </div>
                                                <div className={styles.jobInfo}>
                                                    <h3 className={styles.jobTitle}>{job.title}</h3>
                                                    <p className={styles.companyName}>{job.company_name}</p>
                                                </div>
                                                <div className={styles.jobBadges}>
                                                    {expiringSoon && (
                                                        <span className={styles.urgentBadge}>⏰ 마감임박</span>
                                                    )}
                                                    <div
                                                        className={styles.sourceBadge}
                                                        style={{ backgroundColor: `${source.color}20`, color: source.color }}
                                                    >
                                                        {source.icon} {source.name}
                                                    </div>
                                                </div>
                                            </div>

                                            <div className={styles.jobMeta}>
                                                {job.location && (
                                                    <span className={styles.metaItem}>📍 {job.location}</span>
                                                )}
                                                {job.experience_level && (
                                                    <span className={styles.metaItem}>💼 {job.experience_level}</span>
                                                )}
                                                {job.employment_type && (
                                                    <span className={styles.metaItem}>📋 {job.employment_type}</span>
                                                )}
                                                {job.deadline && (
                                                    <span className={`${styles.metaItem} ${expiringSoon ? styles.urgent : ''}`}>
                                                        📅 ~{job.deadline}
                                                    </span>
                                                )}
                                            </div>

                                            {job.description && (
                                                <p className={styles.jobDescription}>
                                                    {job.description.slice(0, 150)}...
                                                </p>
                                            )}

                                            {job.skills && job.skills.length > 0 && (
                                                <div className={styles.skills}>
                                                    {job.skills.slice(0, 5).map((skill, i) => (
                                                        <span key={i} className={styles.skillTag}>{skill}</span>
                                                    ))}
                                                    {job.skills.length > 5 && (
                                                        <span className={styles.skillMore}>+{job.skills.length - 5}</span>
                                                    )}
                                                </div>
                                            )}

                                            <div className={styles.jobActions}>
                                                <button
                                                    className="btn btn-secondary"
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        setSelectedJob(job);
                                                    }}
                                                >
                                                    상세보기
                                                </button>
                                                <button
                                                    className="btn btn-primary"
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        handleApply(job);
                                                    }}
                                                >
                                                    + 지원 추가
                                                </button>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </>
                    )}

                    {!searched && !loading && (
                        <div className={styles.initialState}>
                            <div className={styles.initialIcon}>🔍</div>
                            <h3>채용공고 검색</h3>
                            <p>키워드를 입력하고 검색 버튼을 클릭하세요</p>
                            <div className={styles.suggestions}>
                                <span>추천 검색어:</span>
                                {['프론트엔드', '백엔드', 'React', 'Python', 'DevOps'].map(kw => (
                                    <button
                                        key={kw}
                                        className={styles.suggestionTag}
                                        onClick={() => {
                                            setSearch({ ...search, keyword: kw });
                                        }}
                                    >
                                        {kw}
                                    </button>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Job Detail Modal */}
            {selectedJob && (
                <div className={styles.modalOverlay} onClick={() => setSelectedJob(null)}>
                    <div className={styles.modal} onClick={e => e.stopPropagation()}>
                        <div className={styles.modalHeader}>
                            <div className={styles.modalTitleSection}>
                                <div className={styles.modalCompanyLogo}>
                                    {selectedJob.company_logo_url ? (
                                        <img src={selectedJob.company_logo_url} alt={selectedJob.company_name} />
                                    ) : (
                                        <span>{selectedJob.company_name[0]}</span>
                                    )}
                                </div>
                                <div>
                                    <h2 className={styles.modalTitle}>{selectedJob.title}</h2>
                                    <p className={styles.modalCompany}>{selectedJob.company_name}</p>
                                </div>
                            </div>
                            <button className={styles.closeBtn} onClick={() => setSelectedJob(null)}>✕</button>
                        </div>

                        <div className={styles.modalBody}>
                            {/* Quick Info */}
                            <div className={styles.quickInfo}>
                                {selectedJob.location && (
                                    <div className={styles.quickInfoItem}>
                                        <span className={styles.quickInfoIcon}>📍</span>
                                        <div>
                                            <span className={styles.quickInfoLabel}>근무지</span>
                                            <span className={styles.quickInfoValue}>{selectedJob.location}</span>
                                        </div>
                                    </div>
                                )}
                                {selectedJob.experience_level && (
                                    <div className={styles.quickInfoItem}>
                                        <span className={styles.quickInfoIcon}>💼</span>
                                        <div>
                                            <span className={styles.quickInfoLabel}>경력</span>
                                            <span className={styles.quickInfoValue}>{selectedJob.experience_level}</span>
                                        </div>
                                    </div>
                                )}
                                {selectedJob.employment_type && (
                                    <div className={styles.quickInfoItem}>
                                        <span className={styles.quickInfoIcon}>📋</span>
                                        <div>
                                            <span className={styles.quickInfoLabel}>고용형태</span>
                                            <span className={styles.quickInfoValue}>{selectedJob.employment_type}</span>
                                        </div>
                                    </div>
                                )}
                                {selectedJob.salary && (
                                    <div className={styles.quickInfoItem}>
                                        <span className={styles.quickInfoIcon}>💰</span>
                                        <div>
                                            <span className={styles.quickInfoLabel}>연봉</span>
                                            <span className={styles.quickInfoValue}>{selectedJob.salary}</span>
                                        </div>
                                    </div>
                                )}
                                {selectedJob.deadline && (
                                    <div className={`${styles.quickInfoItem} ${isExpiringSoon(selectedJob.deadline) ? styles.urgent : ''}`}>
                                        <span className={styles.quickInfoIcon}>📅</span>
                                        <div>
                                            <span className={styles.quickInfoLabel}>마감일</span>
                                            <span className={styles.quickInfoValue}>{formatDate(selectedJob.deadline)}</span>
                                        </div>
                                    </div>
                                )}
                            </div>

                            {/* Skills */}
                            {selectedJob.skills && selectedJob.skills.length > 0 && (
                                <div className={styles.detailSection}>
                                    <h3>🛠️ 기술 스택</h3>
                                    <div className={styles.skillsLarge}>
                                        {selectedJob.skills.map((skill, i) => (
                                            <span key={i} className={styles.skillTagLarge}>{skill}</span>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Description */}
                            {selectedJob.description && (
                                <div className={styles.detailSection}>
                                    <h3>📝 직무 소개</h3>
                                    <p className={styles.detailText}>{selectedJob.description}</p>
                                </div>
                            )}

                            {/* Requirements */}
                            {selectedJob.requirements && (
                                <div className={styles.detailSection}>
                                    <h3>✅ 자격 요건</h3>
                                    <pre className={styles.detailPre}>{selectedJob.requirements}</pre>
                                </div>
                            )}

                            {/* Benefits */}
                            {selectedJob.benefits && (
                                <div className={styles.detailSection}>
                                    <h3>🎁 복리후생</h3>
                                    <pre className={styles.detailPre}>{selectedJob.benefits}</pre>
                                </div>
                            )}

                            {/* Source Info */}
                            <div className={styles.sourceInfo}>
                                <span>출처: {getSourceInfo(selectedJob.source).icon} {getSourceInfo(selectedJob.source).name}</span>
                                {selectedJob.posted_at && (
                                    <span>등록일: {formatDate(selectedJob.posted_at)}</span>
                                )}
                            </div>
                        </div>

                        <div className={styles.modalFooter}>
                            <a
                                href={selectedJob.source_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="btn btn-secondary"
                            >
                                원본 보기 ↗
                            </a>
                            <button
                                className="btn btn-primary"
                                onClick={() => handleApply(selectedJob)}
                            >
                                + 지원 추가
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}
