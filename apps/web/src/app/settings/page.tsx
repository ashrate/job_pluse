'use client';

import Header from '@/components/layout/Header';
import styles from './page.module.css';

export default function SettingsPage() {
    return (
        <>
            <Header title="설정" subtitle="계정 및 연동 설정을 관리하세요" />

            <div className={styles.content}>
                <div className={styles.sections}>
                    {/* Profile Section */}
                    <section className={styles.section}>
                        <h2 className={styles.sectionTitle}>👤 프로필</h2>
                        <div className={styles.card}>
                            <div className={styles.profileHeader}>
                                <div className={styles.avatar}>K</div>
                                <div className={styles.profileInfo}>
                                    <div className={styles.name}>사용자</div>
                                    <div className={styles.email}>user@example.com</div>
                                </div>
                                <button className="btn btn-secondary">수정</button>
                            </div>
                        </div>
                    </section>

                    {/* Target Settings */}
                    <section className={styles.section}>
                        <h2 className={styles.sectionTitle}>🎯 취업 목표</h2>
                        <div className={styles.card}>
                            <div className={styles.formGroup}>
                                <label className={styles.label}>목표 직무</label>
                                <input type="text" className="input" defaultValue="Frontend Engineer" />
                            </div>
                            <div className={styles.formRow}>
                                <div className={styles.formGroup}>
                                    <label className={styles.label}>경력 레벨</label>
                                    <select className="input" defaultValue="junior">
                                        <option value="intern">인턴</option>
                                        <option value="entry">신입</option>
                                        <option value="junior">주니어 (1-3년)</option>
                                        <option value="mid">미드레벨 (4-6년)</option>
                                        <option value="senior">시니어 (7년+)</option>
                                    </select>
                                </div>
                                <div className={styles.formGroup}>
                                    <label className={styles.label}>희망 지역</label>
                                    <input type="text" className="input" defaultValue="서울" />
                                </div>
                            </div>
                            <button className="btn btn-primary">저장</button>
                        </div>
                    </section>

                    {/* Connections */}
                    <section className={styles.section}>
                        <h2 className={styles.sectionTitle}>🔗 연동</h2>
                        <div className={styles.connectionsList}>
                            <div className={styles.connectionCard}>
                                <div className={styles.connectionIcon}>📧</div>
                                <div className={styles.connectionInfo}>
                                    <div className={styles.connectionName}>Gmail</div>
                                    <div className={styles.connectionDesc}>이메일에서 지원 정보를 자동으로 가져옵니다</div>
                                </div>
                                <button className="btn btn-secondary">연동하기</button>
                            </div>

                            <div className={styles.connectionCard}>
                                <div className={styles.connectionIcon}>📅</div>
                                <div className={styles.connectionInfo}>
                                    <div className={styles.connectionName}>Google Calendar</div>
                                    <div className={styles.connectionDesc}>면접 일정을 캘린더에 자동 동기화합니다</div>
                                </div>
                                <button className="btn btn-secondary">연동하기</button>
                            </div>
                        </div>
                    </section>

                    {/* Notifications */}
                    <section className={styles.section}>
                        <h2 className={styles.sectionTitle}>🔔 알림</h2>
                        <div className={styles.card}>
                            <div className={styles.settingRow}>
                                <div className={styles.settingInfo}>
                                    <div className={styles.settingName}>이메일 알림</div>
                                    <div className={styles.settingDesc}>중요 업데이트를 이메일로 받습니다</div>
                                </div>
                                <label className={styles.toggle}>
                                    <input type="checkbox" defaultChecked />
                                    <span className={styles.toggleSlider}></span>
                                </label>
                            </div>

                            <div className={styles.settingRow}>
                                <div className={styles.settingInfo}>
                                    <div className={styles.settingName}>마감 임박 알림</div>
                                    <div className={styles.settingDesc}>마감 3일 전에 알림을 보냅니다</div>
                                </div>
                                <label className={styles.toggle}>
                                    <input type="checkbox" defaultChecked />
                                    <span className={styles.toggleSlider}></span>
                                </label>
                            </div>

                            <div className={styles.settingRow}>
                                <div className={styles.settingInfo}>
                                    <div className={styles.settingName}>면접 리마인더</div>
                                    <div className={styles.settingDesc}>면접 24시간 전에 리마인더를 보냅니다</div>
                                </div>
                                <label className={styles.toggle}>
                                    <input type="checkbox" defaultChecked />
                                    <span className={styles.toggleSlider}></span>
                                </label>
                            </div>
                        </div>
                    </section>

                    {/* Security */}
                    <section className={styles.section}>
                        <h2 className={styles.sectionTitle}>🔒 보안</h2>
                        <div className={styles.card}>
                            <div className={styles.settingRow}>
                                <div className={styles.settingInfo}>
                                    <div className={styles.settingName}>이력서 보관 기간</div>
                                    <div className={styles.settingDesc}>이력서 파일이 자동 삭제되는 기간</div>
                                </div>
                                <select className="input" style={{ width: 'auto' }} defaultValue="30">
                                    <option value="7">7일</option>
                                    <option value="30">30일</option>
                                    <option value="90">90일</option>
                                    <option value="never">무기한</option>
                                </select>
                            </div>
                        </div>
                    </section>

                    {/* Danger Zone */}
                    <section className={styles.section}>
                        <h2 className={styles.sectionTitle}>⚠️ 위험 영역</h2>
                        <div className={`${styles.card} ${styles.dangerCard}`}>
                            <div className={styles.settingRow}>
                                <div className={styles.settingInfo}>
                                    <div className={styles.settingName}>계정 삭제</div>
                                    <div className={styles.settingDesc}>모든 데이터가 영구적으로 삭제됩니다</div>
                                </div>
                                <button className="btn" style={{ background: 'var(--color-error)', color: 'white' }}>
                                    계정 삭제
                                </button>
                            </div>
                        </div>
                    </section>
                </div>
            </div>
        </>
    );
}
