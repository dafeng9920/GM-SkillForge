import React from 'react';
import styles from './DualChannelWorkbench.module.css';

interface DualChannelWorkbenchProps {
    /**
     * The top-level governance data (GateDecision, run_id, evidence)
     */
    headerSlot: React.ReactNode;

    /**
     * Channel A: Cognition / Analysis
     */
    cognitionSlot: React.ReactNode;

    /**
     * Channel B: Execution / Delivery
     */
    executionSlot: React.ReactNode;

    /**
     * The evidence drawer or bottom-level audit data
     */
    footerSlot?: React.ReactNode;
}

export const DualChannelWorkbench: React.FC<DualChannelWorkbenchProps> = ({
    headerSlot,
    cognitionSlot,
    executionSlot,
    footerSlot,
}) => {
    return (
        <div className={styles['workbench-container']}>
            {/* Fixed Governance Header */}
            <header className={styles['workbench-header']}>
                {headerSlot}
            </header>

            {/* Dual Channel Content Area */}
            <main className={styles['workbench-main']}>
                {/* Channel A: Cognition */}
                <section className={`${styles['workbench-channel']} ${styles['channel-cognition']}`}>
                    <div className={styles['channel-header']}>
                        <h2>Cognition (A)</h2>
                        <span className={styles['channel-badge']}>Analysis & Risk</span>
                    </div>
                    <div className={styles['channel-content']}>
                        {cognitionSlot}
                    </div>
                </section>

                {/* Channel Divider */}
                <div className={styles['channel-divider']} aria-hidden="true" />

                {/* Channel B: Execution */}
                <section className={`${styles['workbench-channel']} ${styles['channel-execution']}`}>
                    <div className={styles['channel-header']}>
                        <h2>Execution (B)</h2>
                        <span className={styles['channel-badge']}>Command & Delivery</span>
                    </div>
                    <div className={styles['channel-content']}>
                        {executionSlot}
                    </div>
                </section>
            </main>

            {/* Evidence Footer */}
            {footerSlot && (
                <footer className={styles['workbench-footer']}>
                    {footerSlot}
                </footer>
            )}
        </div>
    );
};
