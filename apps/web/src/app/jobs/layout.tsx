import Sidebar from '@/components/layout/Sidebar';
import styles from '../dashboard/layout.module.css';

export default function JobsLayout({ children }: { children: React.ReactNode }) {
    return (
        <div className={styles.appLayout}>
            <Sidebar />
            <main className={styles.mainContent}>{children}</main>
        </div>
    );
}
