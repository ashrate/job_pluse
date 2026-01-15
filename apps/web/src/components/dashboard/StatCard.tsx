import styles from './StatCard.module.css';

interface StatCardProps {
    icon: string;
    label: string;
    value: number | string;
    trend?: string;
    color?: 'primary' | 'success' | 'warning' | 'error' | 'info';
}

export default function StatCard({ icon, label, value, trend, color = 'primary' }: StatCardProps) {
    return (
        <div className={`${styles.card} ${styles[color]}`}>
            <div className={styles.icon}>{icon}</div>
            <div className={styles.content}>
                <div className={styles.value}>{value}</div>
                <div className={styles.label}>{label}</div>
                {trend && <div className={styles.trend}>{trend}</div>}
            </div>
            <div className={styles.glow}></div>
        </div>
    );
}
