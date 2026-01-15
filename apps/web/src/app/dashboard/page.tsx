'use client';

import { useState } from 'react';
import Header from '@/components/layout/Header';
import StatCard from '@/components/dashboard/StatCard';
import PipelineBoard from '@/components/dashboard/PipelineBoard';
import UpcomingEvents from '@/components/dashboard/UpcomingEvents';
import AddApplicationModal from '@/components/dashboard/AddApplicationModal';
import styles from './page.module.css';

// Sample data
const mockStats = {
    interested: 3,
    applied: 8,
    screening: 4,
    interview_1: 2,
    interview_2: 1,
    offer: 1,
    total: 19,
};

const mockApplications = [
    { id: '1', company: '네이버', position: 'Frontend Engineer', stage: 'interested', appliedAt: null, channel: '직접 지원' },
    { id: '2', company: '카카오', position: 'Software Engineer', stage: 'interested', appliedAt: null, channel: '원티드' },
    { id: '3', company: '라인', position: 'Web Developer', stage: 'interested', appliedAt: null, channel: '잡코리아' },
    { id: '4', company: '쿠팡', position: 'Frontend Developer', stage: 'applied', appliedAt: '2024-01-10', channel: '사람인' },
    { id: '5', company: '배달의민족', position: 'UI Developer', stage: 'applied', appliedAt: '2024-01-09', channel: '직접 지원' },
    { id: '6', company: '토스', position: 'React Developer', stage: 'applied', appliedAt: '2024-01-08', channel: '원티드' },
    { id: '7', company: '당근마켓', position: 'Frontend Engineer', stage: 'applied', appliedAt: '2024-01-07', channel: '잡코리아' },
    { id: '8', company: '무신사', position: 'Web Frontend', stage: 'applied', appliedAt: '2024-01-06', channel: '사람인' },
    { id: '9', company: '야놀자', position: 'Frontend Developer', stage: 'applied', appliedAt: '2024-01-05', channel: '직접 지원' },
    { id: '10', company: '리디', position: 'Web Developer', stage: 'applied', appliedAt: '2024-01-04', channel: '원티드' },
    { id: '11', company: '버킷플레이스', position: 'React Developer', stage: 'applied', appliedAt: '2024-01-03', channel: '잡코리아' },
    { id: '12', company: '삼성전자', position: 'Frontend Engineer', stage: 'screening', appliedAt: '2024-01-02', channel: '사람인' },
    { id: '13', company: 'LG전자', position: 'Web Developer', stage: 'screening', appliedAt: '2024-01-01', channel: '직접 지원' },
    { id: '14', company: 'SK하이닉스', position: 'UI Developer', stage: 'screening', appliedAt: '2023-12-28', channel: '원티드' },
    { id: '15', company: '현대자동차', position: 'Frontend Developer', stage: 'screening', appliedAt: '2023-12-25', channel: '잡코리아' },
    { id: '16', company: '네이버클라우드', position: 'React Developer', stage: 'interview_1', appliedAt: '2023-12-20', channel: '사람인' },
    { id: '17', company: '카카오뱅크', position: 'Frontend Engineer', stage: 'interview_1', appliedAt: '2023-12-18', channel: '직접 지원' },
    { id: '18', company: '토스뱅크', position: 'Web Developer', stage: 'interview_2', appliedAt: '2023-12-15', channel: '원티드' },
    { id: '19', company: '크래프톤', position: 'Frontend Developer', stage: 'offer', appliedAt: '2023-12-10', channel: '잡코리아' },
];

const mockEvents: Array<{ id: string; type: 'interview' | 'deadline'; title: string; date: string; location: string }> = [
    { id: '1', type: 'interview', title: '토스뱅크 2차 면접', date: '2024-01-15 14:00', location: '온라인 (Zoom)' },
    { id: '2', type: 'interview', title: '네이버클라우드 과제 제출', date: '2024-01-16 23:59', location: '이메일 제출' },
    { id: '3', type: 'deadline', title: '크래프톤 오퍼 응답', date: '2024-01-18', location: '' },
];

export default function DashboardPage() {
    const [isModalOpen, setIsModalOpen] = useState(false);

    return (
        <>
            <Header
                title="대시보드"
                subtitle="지원 현황을 한눈에 확인하세요"
                actions={
                    <button
                        className="btn btn-primary"
                        onClick={() => setIsModalOpen(true)}
                    >
                        + 지원 추가
                    </button>
                }
            />

            <div className={styles.content}>
                {/* Stats Section */}
                <section className={styles.statsSection}>
                    <StatCard
                        icon="📊"
                        label="전체 지원"
                        value={mockStats.total}
                        trend="+3 이번 주"
                        color="primary"
                    />
                    <StatCard
                        icon="📝"
                        label="진행중"
                        value={mockStats.applied + mockStats.screening + mockStats.interview_1 + mockStats.interview_2}
                        trend="서류/면접"
                        color="info"
                    />
                    <StatCard
                        icon="📅"
                        label="이번 주 일정"
                        value={mockEvents.length}
                        trend="면접/마감"
                        color="warning"
                    />
                    <StatCard
                        icon="🎉"
                        label="오퍼"
                        value={mockStats.offer}
                        trend="합격!"
                        color="success"
                    />
                </section>

                {/* Main Content Grid */}
                <div className={styles.mainGrid}>
                    {/* Pipeline Board */}
                    <section className={styles.pipelineSection}>
                        <h2 className={styles.sectionTitle}>지원 파이프라인</h2>
                        <PipelineBoard applications={mockApplications} />
                    </section>

                    {/* Sidebar - Upcoming Events */}
                    <aside className={styles.eventsSidebar}>
                        <UpcomingEvents events={mockEvents} />
                    </aside>
                </div>
            </div>

            {/* Add Application Modal */}
            <AddApplicationModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
            />
        </>
    );
}
