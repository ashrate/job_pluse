import styles from './UpcomingEvents.module.css';

interface Event {
    id: string;
    type: 'interview' | 'deadline';
    title: string;
    date: string;
    location: string;
}

interface UpcomingEventsProps {
    events: Event[];
}

export default function UpcomingEvents({ events }: UpcomingEventsProps) {
    return (
        <div className={styles.container}>
            <h2 className={styles.title}>📅 이번 주 일정</h2>

            <div className={styles.eventsList}>
                {events.map((event) => (
                    <div key={event.id} className={`${styles.event} ${styles[event.type]}`}>
                        <div className={styles.eventIcon}>
                            {event.type === 'interview' ? '🎤' : '⏰'}
                        </div>
                        <div className={styles.eventContent}>
                            <div className={styles.eventTitle}>{event.title}</div>
                            <div className={styles.eventDate}>{event.date}</div>
                            {event.location && (
                                <div className={styles.eventLocation}>{event.location}</div>
                            )}
                        </div>
                        <div className={styles.eventBadge}>
                            {event.type === 'interview' ? '면접' : '마감'}
                        </div>
                    </div>
                ))}

                {events.length === 0 && (
                    <div className={styles.empty}>
                        <span className={styles.emptyIcon}>📭</span>
                        <span>예정된 일정이 없습니다</span>
                    </div>
                )}
            </div>
        </div>
    );
}
