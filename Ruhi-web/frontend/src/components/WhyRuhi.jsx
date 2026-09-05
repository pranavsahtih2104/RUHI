import React, { useState } from 'react';
import { ArrowRight, Bot, Compass, CheckCircle2, XCircle, Sparkles } from 'lucide-react';

export default function WhyRuhi() {
  const [activeTab, setActiveTab] = useState('comparison');

  return (
    <section className="ruhi-section" id="why-ruhi">
      <div className="ruhi-container">
        <div className="section-header">
          <div className="section-badge">
            <Compass size={13} />
            <span>THE PARADIGM SHIFT</span>
          </div>
          <h2 className="section-title">Why RUHI?</h2>
          <p className="section-description">
            Traditional AI is a tab you open when you need a quick answer. RUHI is designed to become an integrated personal system that understands your workflows and helps you accomplish real tasks.
          </p>
        </div>

        {/* Interactive Comparison Grid */}
        <div className="why-comparison-grid">
          {/* Box 1: Traditional AI */}
          <div className="comparison-box">
            <div className="comp-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <Bot size={22} color="var(--text-tertiary)" />
                <h3 className="comp-title" style={{ color: 'var(--text-secondary)' }}>AI as a Tool</h3>
              </div>
              <span className="comp-tag" style={{ background: 'rgba(255,255,255,0.05)', color: 'var(--text-tertiary)' }}>
                Conventional
              </span>
            </div>

            <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
              Ephemeral, isolated, and passive. Forgets who you are the moment you close the tab.
            </p>

            <div className="flow-steps">
              <div className="flow-step-item">
                <span style={{ color: 'var(--text-tertiary)', fontFamily: 'var(--font-mono)' }}>01</span>
                <span>User asks a question</span>
              </div>
              <div className="flow-step-item">
                <span style={{ color: 'var(--text-tertiary)', fontFamily: 'var(--font-mono)' }}>02</span>
                <span>Model predicts text string</span>
              </div>
              <div className="flow-step-item">
                <span style={{ color: 'var(--text-tertiary)', fontFamily: 'var(--font-mono)' }}>03</span>
                <span>User copies text and does all manual work</span>
              </div>
            </div>

            <div className="comp-summary">
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#f87171', fontSize: '0.84rem' }}>
                <XCircle size={16} />
                <span>No digital environment awareness or execution capability</span>
              </div>
            </div>
          </div>

          {/* Box 2: RUHI Personal AI System */}
          <div className="comparison-box ruhi-box">
            <div className="comp-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <Sparkles size={22} color="var(--cyan-primary)" />
                <h3 className="comp-title text-gradient-cyan">RUHI as a Personal System</h3>
              </div>
              <span className="comp-tag status-available">
                Intelligent Layer
              </span>
            </div>

            <p style={{ fontSize: '0.9rem', color: 'var(--text-primary)' }}>
              Continuous, context-aware, and actionable. Evolves alongside your projects.
            </p>

            <div className="flow-steps">
              <div className="flow-step-item highlight">
                <span style={{ fontFamily: 'var(--font-mono)' }}>01</span>
                <span>User shares intent or goal</span>
              </div>
              <div className="flow-step-item highlight">
                <span style={{ fontFamily: 'var(--font-mono)' }}>02</span>
                <span>RUHI retains context, retrieves knowledge & reasons</span>
              </div>
              <div className="flow-step-item highlight">
                <span style={{ fontFamily: 'var(--font-mono)' }}>03</span>
                <span>Selects tools, prepares plans, and coordinates actions</span>
              </div>
            </div>

            <div className="comp-summary">
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#34d399', fontSize: '0.84rem' }}>
                <CheckCircle2 size={16} />
                <span>"Don't just ask AI questions. Let RUHI help you get things done."</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
