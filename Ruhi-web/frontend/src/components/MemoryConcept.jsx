import React from 'react';
import { Database, Clock, Lock, Sparkles, Check, ArrowRight } from 'lucide-react';

export default function MemoryConcept() {
  return (
    <section className="ruhi-section" id="memory-concept">
      <div className="ruhi-container">
        <div className="section-header">
          <div className="section-badge">
            <Database size={13} />
            <span>CONTINUITY ARCHITECTURE</span>
          </div>
          <h2 className="section-title">The RUHI Memory System</h2>
          <p className="section-description">
            Intelligence without memory is merely a static text generator. RUHI is designed with a multi-tiered memory architecture that respects your privacy and evolves with your life.
          </p>
        </div>

        <div className="memory-concept-grid">
          {/* Box 1: Short-term Session Context */}
          <div className="memory-box">
            <div className="memory-box-header">
              <div>
                <span className="status-pill status-available" style={{ marginBottom: '8px' }}>
                  <Check size={10} />
                  <span>Active Now in Web</span>
                </span>
                <h3 style={{ fontSize: '1.3rem', fontWeight: 700, color: 'var(--text-pure)' }}>
                  Short-Term Context
                </h3>
              </div>
              <Clock size={24} color="var(--cyan-primary)" />
            </div>

            <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
              Maintains the working thread of thoughts during your active session. Tracks pronouns, references previous messages, and preserves multi-turn reasoning continuity.
            </p>

            <div className="memory-slots-list">
              <div className="memory-slot-item">
                <span style={{ color: 'var(--text-primary)' }}>Session Context Window</span>
                <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--cyan-primary)' }}>30 Turns Active</span>
              </div>
              <div className="memory-slot-item">
                <span style={{ color: 'var(--text-primary)' }}>Ephemerality</span>
                <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-tertiary)' }}>Auto-clears on exit</span>
              </div>
              <div className="memory-slot-item">
                <span style={{ color: 'var(--text-primary)' }}>User Control</span>
                <span style={{ fontFamily: 'var(--font-mono)', color: '#34d399' }}>Instant One-Click Reset</span>
              </div>
            </div>
          </div>

          {/* Box 2: Long-term Personal Memory */}
          <div className="memory-box" style={{ borderColor: 'rgba(168, 85, 247, 0.3)' }}>
            <div className="memory-box-header">
              <div>
                <span className="status-pill status-coming-soon" style={{ marginBottom: '8px' }}>
                  <Clock size={10} />
                  <span>Planned Architecture</span>
                </span>
                <h3 style={{ fontSize: '1.3rem', fontWeight: 700, color: 'var(--text-pure)' }}>
                  Long-Term Personal Memory
                </h3>
              </div>
              <Sparkles size={24} color="var(--violet-bright)" />
            </div>

            <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
              Retains persistent knowledge across sessions: your working styles, coding preferences, project definitions, and personal guidelines.
            </p>

            <div className="memory-slots-list">
              <div className="memory-slot-item">
                <span style={{ color: 'var(--text-primary)' }}>Knowledge Vectors</span>
                <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--violet-bright)' }}>Local Vector DB</span>
              </div>
              <div className="memory-slot-item">
                <span style={{ color: 'var(--text-primary)' }}>Memory Inspector</span>
                <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>View, Edit & Delete</span>
              </div>
              <div className="memory-slot-item">
                <span style={{ color: 'var(--text-primary)' }}>Privacy Boundary</span>
                <span style={{ fontFamily: 'var(--font-mono)', color: '#34d399' }}>Encrypted on Device</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
