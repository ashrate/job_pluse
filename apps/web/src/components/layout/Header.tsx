'use client';

import styles from './Header.module.css';

interface HeaderProps {
    title: string;
    subtitle?: string;
    actions?: React.ReactNode;
}

export default function Header({ title, subtitle, actions }: HeaderProps) {
    return (
        <header className={styles.header}>
            <div className={styles.left}>
                <h1 className={styles.title}>{title}</h1>
                {subtitle && <p className={styles.subtitle}>{subtitle}</p>}
            </div>
            <div className={styles.right}>
                {actions}
                <button className={styles.notificationBtn} aria-label="알림">
                    🔔
                </button>
            </div>
        </header>
    );
}
