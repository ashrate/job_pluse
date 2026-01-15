'use client';

import { useMemo } from 'react';
import styles from './PipelineBoard.module.css';

interface Application {
    id: string;
    company: string;
    position: string;
    stage: string;
    appliedAt: string | null;
    channel: string;
}

interface PipelineBoardProps {
    applications: Application[];
}

const stages = [
    { key: 'interested', label: '관심', icon: '⭐' },
    { key: 'applied', label: '지원완료', icon: '📨' },
    { key: 'screening', label: '서류심사', icon: '📋' },
    { key: 'interview_1', label: '1차 면접', icon: '🎤' },
    { key: 'interview_2', label: '2차 면접', icon: '🎯' },
    { key: 'offer', label: '오퍼', icon: '🎉' },
];

export default function PipelineBoard({ applications }: PipelineBoardProps) {
    const groupedApplications = useMemo(() => {
        const grouped: Record<string, Application[]> = {};
        stages.forEach(stage => {
            grouped[stage.key] = applications.filter(app => app.stage === stage.key);
        });
        return grouped;
    }, [applications]);

    return (
        <div className={styles.board}>
            {stages.map((stage) => (
                <div key={stage.key} className={styles.column}>
                    <div className={styles.columnHeader}>
                        <div className={styles.columnTitle}>
                            <span className={styles.columnIcon}>{stage.icon}</span>
                            <span>{stage.label}</span>
                        </div>
                        <span className={styles.columnCount}>
                            {groupedApplications[stage.key]?.length || 0}
                        </span>
                    </div>
                    <div className={styles.columnCards}>
                        {groupedApplications[stage.key]?.map((app) => (
                            <div key={app.id} className={styles.card}>
                                <div className={styles.cardCompany}>{app.company}</div>
                                <div className={styles.cardPosition}>{app.position}</div>
                                <div className={styles.cardFooter}>
                                    <span className={styles.cardChannel}>{app.channel}</span>
                                    {app.appliedAt && (
                                        <span className={styles.cardDate}>{app.appliedAt}</span>
                                    )}
                                </div>
                            </div>
                        ))}
                        {(!groupedApplications[stage.key] || groupedApplications[stage.key].length === 0) && (
                            <div className={styles.emptyColumn}>
                                아직 없음
                            </div>
                        )}
                    </div>
                </div>
            ))}
        </div>
    );
}
