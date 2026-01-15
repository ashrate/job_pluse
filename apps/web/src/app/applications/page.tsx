'use client';

import Header from '@/components/layout/Header';
import PipelineBoard from '@/components/dashboard/PipelineBoard';
import styles from './page.module.css';

const mockApplications = [
    { id: '1', company: '네이버', position: 'Frontend Engineer', stage: 'interested', appliedAt: null, channel: '직접 지원' },
    { id: '2', company: '카카오', position: 'Software Engineer', stage: 'interested', appliedAt: null, channel: '원티드' },
    { id: '3', company: '라인', position: 'Web Developer', stage: 'interested', appliedAt: null, channel: '잡코리아' },
    { id: '4', company: '쿠팡', position: 'Frontend Developer', stage: 'applied', appliedAt: '2024-01-10', channel: '사람인' },
    { id: '5', company: '배달의민족', position: 'UI Developer', stage: 'applied', appliedAt: '2024-01-09', channel: '직접 지원' },
    { id: '6', company: '토스', position: 'React Developer', stage: 'applied', appliedAt: '2024-01-08', channel: '원티드' },
    { id: '7', company: '당근마켓', position: 'Frontend Engineer', stage: 'applied', appliedAt: '2024-01-07', channel: '잡코리아' },
    { id: '8', company: '삼성전자', position: 'Frontend Engineer', stage: 'screening', appliedAt: '2024-01-02', channel: '사람인' },
    { id: '9', company: 'LG전자', position: 'Web Developer', stage: 'screening', appliedAt: '2024-01-01', channel: '직접 지원' },
    { id: '10', company: '네이버클라우드', position: 'React Developer', stage: 'interview_1', appliedAt: '2023-12-20', channel: '사람인' },
    { id: '11', company: '카카오뱅크', position: 'Frontend Engineer', stage: 'interview_1', appliedAt: '2023-12-18', channel: '직접 지원' },
    { id: '12', company: '토스뱅크', position: 'Web Developer', stage: 'interview_2', appliedAt: '2023-12-15', channel: '원티드' },
    { id: '13', company: '크래프톤', position: 'Frontend Developer', stage: 'offer', appliedAt: '2023-12-10', channel: '잡코리아' },
];

export default function ApplicationsPage() {
    return (
        <>
            <Header
                title="지원현황"
                subtitle="모든 지원 내역을 관리하세요"
                actions={
                    <>
                        <button className="btn btn-secondary">필터</button>
                        <button className="btn btn-primary">+ 지원 추가</button>
                    </>
                }
            />

            <div className={styles.content}>
                <div className={styles.tabs}>
                    <button className={`${styles.tab} ${styles.active}`}>칸반 보드</button>
                    <button className={styles.tab}>리스트</button>
                    <button className={styles.tab}>캘린더</button>
                </div>

                <div className={styles.boardWrapper}>
                    <PipelineBoard applications={mockApplications} />
                </div>
            </div>
        </>
    );
}
