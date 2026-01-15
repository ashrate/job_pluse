'use client';

import { useState } from 'react';
import styles from './AddApplicationModal.module.css';

interface AddApplicationModalProps {
    isOpen: boolean;
    onClose: () => void;
}

export default function AddApplicationModal({ isOpen, onClose }: AddApplicationModalProps) {
    const [formData, setFormData] = useState({
        companyName: '',
        positionTitle: '',
        stage: 'interested',
        channel: '',
        jobUrl: '',
        notes: '',
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        // TODO: API call to create application
        console.log('Creating application:', formData);
        onClose();
    };

    if (!isOpen) return null;

    return (
        <div className={`${styles.overlay} ${isOpen ? styles.active : ''}`} onClick={onClose}>
            <div className={styles.modal} onClick={e => e.stopPropagation()}>
                <div className={styles.header}>
                    <h2 className={styles.title}>새 지원 추가</h2>
                    <button className={styles.closeBtn} onClick={onClose}>✕</button>
                </div>

                <form className={styles.body} onSubmit={handleSubmit}>
                    <div className={styles.formGroup}>
                        <label className={styles.label}>회사명 *</label>
                        <input
                            type="text"
                            className="input"
                            placeholder="예: 네이버"
                            value={formData.companyName}
                            onChange={e => setFormData({ ...formData, companyName: e.target.value })}
                            required
                        />
                    </div>

                    <div className={styles.formGroup}>
                        <label className={styles.label}>포지션</label>
                        <input
                            type="text"
                            className="input"
                            placeholder="예: Frontend Engineer"
                            value={formData.positionTitle}
                            onChange={e => setFormData({ ...formData, positionTitle: e.target.value })}
                        />
                    </div>

                    <div className={styles.formRow}>
                        <div className={styles.formGroup}>
                            <label className={styles.label}>상태</label>
                            <select
                                className="input"
                                value={formData.stage}
                                onChange={e => setFormData({ ...formData, stage: e.target.value })}
                            >
                                <option value="interested">관심</option>
                                <option value="applied">지원완료</option>
                                <option value="screening">서류심사</option>
                                <option value="interview_1">1차 면접</option>
                                <option value="interview_2">2차 면접</option>
                                <option value="offer">오퍼</option>
                            </select>
                        </div>

                        <div className={styles.formGroup}>
                            <label className={styles.label}>지원 경로</label>
                            <input
                                type="text"
                                className="input"
                                placeholder="예: 원티드"
                                value={formData.channel}
                                onChange={e => setFormData({ ...formData, channel: e.target.value })}
                            />
                        </div>
                    </div>

                    <div className={styles.formGroup}>
                        <label className={styles.label}>공고 URL</label>
                        <input
                            type="url"
                            className="input"
                            placeholder="https://..."
                            value={formData.jobUrl}
                            onChange={e => setFormData({ ...formData, jobUrl: e.target.value })}
                        />
                    </div>

                    <div className={styles.formGroup}>
                        <label className={styles.label}>메모</label>
                        <textarea
                            className={`input ${styles.textarea}`}
                            placeholder="추가 메모..."
                            rows={3}
                            value={formData.notes}
                            onChange={e => setFormData({ ...formData, notes: e.target.value })}
                        />
                    </div>

                    <div className={styles.footer}>
                        <button type="button" className="btn btn-secondary" onClick={onClose}>
                            취소
                        </button>
                        <button type="submit" className="btn btn-primary">
                            추가하기
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
