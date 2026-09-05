import React from 'react';
import { ArrowUp, Sparkles, Terminal, Code } from 'lucide-react';

export default function Footer({ onOpenInstallModal }) {
  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <footer className="ruhi-footer">
      <div className="ruhi-container">
        <div className="footer-grid">
          {/* Column 1: Brand & Philosophy */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '14px' }}>
              <img src="/ruhi-icon.svg" alt="RUHI Emblem" style={{ width: '28px', height: '28px' }} />
              <span className="brand-text" style={{ fontSize: '1.25rem' }}>RUHI</span>
            </div>
            <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', lineHeight: 1.6, maxWidth: '320px' }}>
              An intelligent personal AI system designed to become the cognitive layer across your digital life.
            </p>
            <div style={{ marginTop: '16px', display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--cyan-primary)', fontSize: '0.78rem', fontFamily: 'var(--font-mono)' }}>
              <Sparkles size={14} />
              <span>An AI that grows with you.</span>
            </div>
          </div>

          {/* Column 2: System */}
          <div>
            <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-pure)', marginBottom: '16px', letterSpacing: '0.04em' }}>
              System
            </h4>
            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '0.84rem' }}>
              <li><a href="#what-is-ruhi">What is RUHI?</a></li>
              <li><a href="#why-ruhi">Why RUHI?</a></li>
              <li><a href="#capabilities">Capability Matrix</a></li>
              <li><a href="#how-it-works">9-Stage Pipeline</a></li>
            </ul>
          </div>

          {/* Column 3: Ecosystem */}
          <div>
            <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-pure)', marginBottom: '16px', letterSpacing: '0.04em' }}>
              Ecosystem
            </h4>
            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '0.84rem' }}>
              <li><a href="#try-ruhi">Web Experience</a></li>
              <li><a href="#desktop-ruhi">Desktop Companion</a></li>
              <li><a href="#memory-concept">Memory Architecture</a></li>
              <li><a href="#comparison-matrix">Web vs Desktop</a></li>
            </ul>
          </div>

          {/* Column 4: Trust & Code */}
          <div>
            <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-pure)', marginBottom: '16px', letterSpacing: '0.04em' }}>
              Trust & Source
            </h4>
            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '0.84rem' }}>
              <li><a href="#privacy">Privacy & Control</a></li>
              <li><button onClick={onOpenInstallModal} style={{ color: 'var(--text-secondary)', fontSize: '0.84rem' }}>Download Desktop</button></li>
              <li><a href="https://github.com" target="_blank" rel="noopener noreferrer" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><span>GitHub Repo</span></a></li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="footer-bottom">
          <div>
            © {new Date().getFullYear()} RUHI Personal AI System. All rights reserved. Built with precision.
          </div>
          <button 
            onClick={scrollToTop}
            style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--text-secondary)', fontSize: '0.8rem' }}
          >
            <span>Back to top</span>
            <ArrowUp size={14} />
          </button>
        </div>
      </div>
    </footer>
  );
}
