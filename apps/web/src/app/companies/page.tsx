'use client';

import { useState } from 'react';
import Header from '@/components/layout/Header';
import styles from './page.module.css';

const mockCompanies = [
    { id: '1', name: '네이버', domain: 'naver.com', activeJobs: 15, logo: '🟢' },
    { id: '2', name: '카카오', domain: 'kakao.com', activeJobs: 12, logo: '💬' },
    { id: '3', name: '라인', domain: 'line.me', activeJobs: 8, logo: '💚' },
    { id: '4', name: '쿠팡', domain: 'coupang.com', activeJobs: 23, logo: '🟠' },
    { id: '5', name: '배달의민족', domain: 'baemin.com', activeJobs: 10, logo: '🍽️' },
    { id: '6', name: '토스', domain: 'toss.im', activeJobs: 18, logo: '🔵' },
];

export default function CompaniesPage() {
    const [searchQuery, setSearchQuery] = useState('');

    const filteredCompanies = mockCompanies.filter(c =>
        c.name.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
        <>
            <Header title="기업" subtitle="관심 기업의 정보를 확인하세요" />

            <div className={styles.content}>
                <div className={styles.searchBar}>
                    <span className={styles.searchIcon}>🔍</span>
                    <input
                        type="text"
                        className={styles.searchInput}
                        placeholder="기업명으로 검색..."
                        value={searchQuery}
                        onChange={e => setSearchQuery(e.target.value)}
                    />
                </div>

                <div className={styles.companiesGrid}>
                    {filteredCompanies.map(company => (
                        <div key={company.id} className={styles.companyCard}>
                            <div className={styles.companyLogo}>{company.logo}</div>
                            <div className={styles.companyInfo}>
                                <h3 className={styles.companyName}>{company.name}</h3>
                                <p className={styles.companyDomain}>{company.domain}</p>
                            </div>
                            <div className={styles.companyMeta}>
                                <span className={styles.jobCount}>{company.activeJobs}개 채용중</span>
                            </div>
                            <button className="btn btn-secondary">상세보기</button>
                        </div>
                    ))}
                </div>

                {filteredCompanies.length === 0 && (
                    <div className={styles.emptyState}>
                        <span className={styles.emptyIcon}>🔍</span>
                        <p>검색 결과가 없습니다</p>
                    </div>
                )}
            </div>
        </>
    );
}
