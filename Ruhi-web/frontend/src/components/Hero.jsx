import React from 'react';
import { Sparkles, ArrowRight, ShieldCheck, Cpu, Terminal } from 'lucide-react';
import RuhiCoreOrb from './RuhiCoreOrb';

export default function Hero({ onExploreClick, onTryClick }) {
  return (
    <header className="hero-section" id="hero">
      <div className="ruhi-container hero-grid">
        {/* Left Column: Hero Copy & Value Proposition */}
        <div className="hero-content">
          <div className="hero-badge">
            <span className="hero-badge-pulse" />
            <span>THE PERSONAL AI LAYER</span>
          </div>

          <h1 className="hero-title">
            RUHI
            <br />
            <span className="text-gradient-cyan">Your Personal AI.</span>
          </h1>

          <p className="hero-subtitle">
            An intelligent layer between you and your digital life. RUHI understands your intent, remembers relevant context, reasons through complex tasks, and helps you get things done.
          </p>

          <div className="hero-actions">
            <button 
              onClick={onExploreClick}
              className="btn-primary"
              aria-label="Meet RUHI Architecture"
            >
              <span>Meet RUHI</span>
              <ArrowRight size={18} />
            </button>

            <button 
              onClick={onTryClick}
              className="btn-secondary"
              aria-label="Experience Web RUHI Chat"
            >
              <Sparkles size={18} className="text-gradient-cyan" />
              <span>Try RUHI Now</span>
            </button>
          </div>

          <div className="hero-stats">
            <div className="stat-item">
              <span className="stat-number text-gradient-cyan">System Layer</span>
              <span className="stat-label">Beyond Chatbots</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">Contextual</span>
              <span className="stat-label">Session Memory</span>
            </div>
            <div className="stat-item">
              <span className="stat-number text-gradient-purple">Extensible</span>
              <span className="stat-label">Desktop Tools</span>
            </div>
          </div>
        </div>

        {/* Right Column: Dynamic Neural Core Orb Visual */}
        <div className="hero-visual-wrapper">
          <RuhiCoreOrb state="idle" size={400} />
        </div>
      </div>
    </header>
  );
}
