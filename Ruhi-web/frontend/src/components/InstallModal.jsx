import React, { useState } from 'react';
import { X, ShieldCheck, Apple, Monitor, Terminal, CheckCircle2, Folder, Mic, Cpu, Clock, Layers, Sparkles } from 'lucide-react';

export default function InstallModal({ isOpen, onClose }) {
  const [selectedOS, setSelectedOS] = useState('mac');

  if (!isOpen) return null;

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button 
          className="modal-close-btn" 
          onClick={onClose}
          aria-label="Close Modal"
        >
          <X size={20} />
        </button>

        {/* Modal Header */}
        <div style={{ textAlign: 'center', marginBottom: '24px' }}>
          <div className="hero-badge" style={{ marginBottom: '12px' }}>
            <Clock size={14} />
            <span>RUHI DESKTOP // COMING SOON</span>
          </div>
          <h2 style={{ fontSize: '1.75rem', fontWeight: 800, marginBottom: '8px' }}>
            RUHI Desktop Application
          </h2>
          <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', maxWidth: '440px', margin: '0 auto' }}>
            The native desktop application will bring RUHI Core directly to your computer, enabling permission-guarded filesystem access and local workflows.
          </p>
        </div>

        {/* OS Platform Target */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px', marginBottom: '20px' }}>
          <button
            onClick={() => setSelectedOS('mac')}
            className={`filter-pill ${selectedOS === 'mac' ? 'active' : ''}`}
            style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', padding: '10px' }}
          >
            <Apple size={16} />
            <span>macOS</span>
          </button>
          <button
            onClick={() => setSelectedOS('win')}
            className={`filter-pill ${selectedOS === 'win' ? 'active' : ''}`}
            style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', padding: '10px' }}
          >
            <Monitor size={16} />
            <span>Windows</span>
          </button>
          <button
            onClick={() => setSelectedOS('linux')}
            className={`filter-pill ${selectedOS === 'linux' ? 'active' : ''}`}
            style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', padding: '10px' }}
          >
            <Terminal size={16} />
            <span>Linux</span>
          </button>
        </div>

        {/* Architecture Specs */}
        <div style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-lg)', padding: '20px', marginBottom: '20px' }}>
          <h4 style={{ fontSize: '0.92rem', fontWeight: 700, marginBottom: '8px', color: 'var(--text-pure)', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <ShieldCheck size={16} color="#34d399" />
            <span>Desktop Architecture & Security Model</span>
          </h4>
          
          <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
            <li style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
              <CheckCircle2 size={14} color="var(--cyan-primary)" style={{ marginTop: '2px', flexShrink: 0 }} />
              <span><strong>Shared RUHI Core:</strong> Seamlessly reuses the same intelligence, context, and memory layer present in RUHI Web.</span>
            </li>
            <li style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
              <CheckCircle2 size={14} color="var(--cyan-primary)" style={{ marginTop: '2px', flexShrink: 0 }} />
              <span><strong>Explicit Permission Engine:</strong> No unprompted filesystem reads, writes, or process executions. Every action is gated by transparent user consent.</span>
            </li>
            <li style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
              <CheckCircle2 size={14} color="var(--cyan-primary)" style={{ marginTop: '2px', flexShrink: 0 }} />
              <span><strong>Local Vector Store:</strong> On-device document search and persistent memory without cloud data lock-in.</span>
            </li>
          </ul>
        </div>

        {/* Notification Status Info */}
        <div style={{ background: 'rgba(0, 242, 254, 0.04)', border: '1px solid rgba(0, 242, 254, 0.2)', borderRadius: 'var(--radius-md)', padding: '14px', textAlign: 'center', marginBottom: '16px' }}>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-primary)', fontWeight: 600 }}>
            ✨ RUHI Web v1 is live now in your browser.
          </span>
          <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
            The native desktop installer builds will be made available as development progresses.
          </p>
        </div>

        <button 
          onClick={onClose}
          className="btn-primary" 
          style={{ width: '100%', padding: '12px', fontSize: '0.95rem' }}
        >
          <span>Continue Exploring RUHI Web</span>
        </button>
      </div>
    </div>
  );
}
