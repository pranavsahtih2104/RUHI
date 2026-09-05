import React, { useState } from 'react';
import { Brain, Database, Wrench, ChevronRight, Zap, Eye, Sparkles } from 'lucide-react';

export default function WhatIsRuhi() {
  const [activeBranch, setActiveBranch] = useState('ai');

  const branches = {
    ai: {
      title: 'AI & Reasoning',
      subtitle: 'Cognitive Layer',
      icon: <Brain size={22} />,
      desc: 'RUHI does not just predict the next token. It deconstructs multi-step objectives into structured plans, analyzes trade-offs, and reasons before taking action.',
      details: [
        'Multi-step goal decomposition',
        'Model provider decoupling (Gemini, Claude, local models)',
        'Iterative self-critique and validation',
      ],
    },
    memory: {
      title: 'Memory & Context',
      subtitle: 'Continuity Layer',
      icon: <Database size={22} />,
      desc: 'Maintains active conversational state across turns and synthesizes long-term preferences, project knowledge, and personal guidelines into accessible context.',
      details: [
        'Active session sliding-window context',
        'Transparent, inspectable memory slots',
        'Explicit user privacy and data retention controls',
      ],
    },
    tools: {
      title: 'Tools & Actions',
      subtitle: 'Execution Layer',
      icon: <Wrench size={22} />,
      desc: 'Connects intelligence to execution. Coordinates web information retrieval, script generation, and installed desktop automation with strict user authorization.',
      details: [
        'Extensible tool registry architecture',
        'Permission-guarded desktop workflows',
        'Auditable action logs for safety',
      ],
    },
  };

  return (
    <section className="ruhi-section" id="what-is-ruhi">
      <div className="ruhi-container">
        <div className="section-header">
          <div className="section-badge">
            <Sparkles size={13} />
            <span>SYSTEM ARCHITECTURE</span>
          </div>
          <h2 className="section-title">What is RUHI?</h2>
          <p className="section-description">
            RUHI is being built as an integrated personal AI system that goes far beyond asking questions. It bridges intelligence, personal continuity, and autonomous execution.
          </p>
        </div>

        {/* Visual Architecture Diagram */}
        <div className="arch-diagram-wrapper">
          {/* Top Node */}
          <div className="arch-root-node">
            <div className="node-chip-core">
              RUHI SYSTEM CORE
            </div>
            <div className="arch-connect-stem" />
          </div>

          {/* Tri-Branch Grid */}
          <div className="arch-branches-grid">
            {Object.entries(branches).map(([key, data]) => {
              const isSelected = activeBranch === key;
              return (
                <div
                  key={key}
                  onClick={() => setActiveBranch(key)}
                  className={`arch-card-node ${isSelected ? 'active' : ''}`}
                  role="button"
                  tabIndex={0}
                  aria-label={`Inspect ${data.title}`}
                  onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') setActiveBranch(key); }}
                >
                  <div className="node-header">
                    <span className="text-gradient-cyan" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      {data.icon}
                      <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', textTransform: 'uppercase' }}>
                        {data.subtitle}
                      </span>
                    </span>
                    <ChevronRight size={16} color={isSelected ? 'var(--cyan-primary)' : 'var(--text-tertiary)'} />
                  </div>

                  <h3 className="node-title">{data.title}</h3>
                  <p className="node-desc">{data.desc}</p>

                  {isSelected && (
                    <ul style={{ marginTop: '16px', listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                      {data.details.map((item, i) => (
                        <li key={i} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.8rem', color: 'var(--text-primary)' }}>
                          <Zap size={12} color="var(--cyan-primary)" />
                          <span>{item}</span>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              );
            })}
          </div>

          {/* Bottom Summary Bar */}
          <div className="arch-output-bar">
            <span>✨ An Integrated Personal AI Layer That Grows With You</span>
          </div>
        </div>
      </div>
    </section>
  );
}
