'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import styles from './Sidebar.module.css';

const navItems = [
    {
        section: '메인',
        items: [
            { href: '/dashboard', label: '대시보드', icon: '📊' },
            { href: '/applications', label: '지원현황', icon: '📋' },
        ]
    },
    {
        section: '리서치',
        items: [
            { href: '/companies', label: '기업', icon: '🏢' },
            { href: '/jobs', label: '공고', icon: '💼' },
        ]
    },
    {
        section: '도구',
        items: [
            { href: '/resumes', label: '이력서', icon: '📄' },
        ]
    },
    {
        section: '설정',
        items: [
            { href: '/settings', label: '설정', icon: '⚙️' },
        ]
    }
];

export default function Sidebar() {
    const pathname = usePathname();

    return (
        <aside className={styles.sidebar}>
            <div className={styles.logo}>
                <Link href="/dashboard">
                    <div className={styles.logoIcon}>🚀</div>
                    <span>JobPulse</span>
                </Link>
            </div>

            <nav className={styles.nav}>
                {navItems.map((section) => (
                    <div key={section.section} className={styles.navSection}>
                        <div className={styles.navSectionTitle}>{section.section}</div>
                        {section.items.map((item) => (
                            <Link
                                key={item.href}
                                href={item.href}
                                className={`${styles.navItem} ${pathname === item.href ? styles.active : ''}`}
                            >
                                <span className={styles.navItemIcon}>{item.icon}</span>
                                <span>{item.label}</span>
                            </Link>
                        ))}
                    </div>
                ))}
            </nav>

            <div className={styles.userSection}>
                <div className={styles.userAvatar}>K</div>
                <div className={styles.userInfo}>
                    <div className={styles.userName}>사용자</div>
                    <div className={styles.userEmail}>user@example.com</div>
                </div>
            </div>
        </aside>
    );
}
