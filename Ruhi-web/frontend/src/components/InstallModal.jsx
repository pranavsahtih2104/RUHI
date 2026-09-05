import React, { useState } from 'react';
import { X, Download, ShieldCheck, Apple, Monitor, Terminal, CheckCircle2, Folder, Mic, Cpu } from 'lucide-react';

export default function InstallModal({ isOpen, onClose }) {
  const [selectedOS, setSelectedOS] = useState('mac');
  const [permissions, setPermissions] = useState({
    files: true,
    apps: true,
    mic: false,
    automation: true,
  });
  const [downloadStarted, setDownloadStarted] = useState(false);

  if (!isOpen) return null;

  const togglePerm = (key) => {
    setPermissions(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const handleDownload = () => {
    setDownloadStarted(true);
    setTimeout(() => setDownloadStarted(false), 4000);
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button 
          className="modal-close-btn" 
          onClick={onClose}
          aria-label="Close Install Modal"
        >
          <X size={20} />
        </button>

        {/* Modal Header */}
        <div style={{ textAlign: 'center', marginBottom: '24px' }}>
          <div className="hero-badge" style={{ marginBottom: '12px' }}>
            <ShieldCheck size={14} />
            <span>DESKTOP RUNTIME // EARLY ACCESS</span>
          </div>
          <h2 style={{ fontSize: '1.8rem', fontWeight: 800, marginBottom: '8px' }}>
            Install RUHI on Your Machine
          </h2>
          <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
            Unlock local file access, application orchestration, and background workflows with explicit permission control.
          </p>
        </div>

        {/* OS Selector */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px', marginBottom: '24px' }}>
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

        {/* Permission Setup Preview */}
        <div style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-lg)', padding: '20px', marginBottom: '24px' }}>
          <h4 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: '4px', color: 'var(--text-pure)' }}>
            Initial Permission Preferences
          </h4>
          <p style={{ fontSize: '0.78rem', color: 'var(--text-tertiary)', marginBottom: '16px' }}>
            Choose which capabilities RUHI may request when installed:
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.84rem' }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Folder size={14} color="var(--cyan-primary)" />
                <span>Local Files & Workspaces</span>
              </span>
              <button 
                onClick={() => togglePerm('files')}
                className={`perm-toggle-btn ${permissions.files ? 'allowed' : 'blocked'}`}
                style={{ padding: '4px 10px', fontSize: '0.7rem' }}
              >
                {permissions.files ? 'Allowed' : 'Don\'t Allow'}
              </button>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.84rem' }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Terminal size={14} color="var(--cyan-primary)" />
                <span>Application Execution</span>
              </span>
              <button 
                onClick={() => togglePerm('apps')}
                className={`perm-toggle-btn ${permissions.apps ? 'allowed' : 'blocked'}`}
                style={{ padding: '4px 10px', fontSize: '0.7rem' }}
              >
                {permissions.apps ? 'Allowed' : 'Don\'t Allow'}
              </button>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.84rem' }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Mic size={14} color="var(--cyan-primary)" />
                <span>Microphone & Voice</span>
              </span>
              <button 
                onClick={() => togglePerm('mic')}
                className={`perm-toggle-btn ${permissions.mic ? 'allowed' : 'blocked'}`}
                style={{ padding: '4px 10px', fontSize: '0.7rem' }}
              >
                {permissions.mic ? 'Allowed' : 'Don\'t Allow'}
              </button>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.84rem' }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Cpu size={14} color="var(--cyan-primary)" />
                <span>Background Automation</span>
              </span>
              <button 
                onClick={() => togglePerm('automation')}
                className={`perm-toggle-btn ${permissions.automation ? 'allowed' : 'blocked'}`}
                style={{ padding: '4px 10px', fontSize: '0.7rem' }}
              >
                {permissions.automation ? 'Allowed' : 'Don\'t Allow'}
              </button>
            </div>
          </div>
        </div>

        {/* Action Button */}
        <button 
          onClick={handleDownload}
          className="btn-primary" 
          style={{ width: '100%', padding: '14px', fontSize: '1rem' }}
        >
          {downloadStarted ? (
            <>
              <CheckCircle2 size={18} color="#040812" />
              <span>Preparing RUHI Installer Package...</span>
            </>
          ) : (
            <>
              <Download size={18} />
              <span>Download RUHI for {selectedOS === 'mac' ? 'macOS (Universal DMG)' : selectedOS === 'win' ? 'Windows (x64 EXE)' : 'Linux (AppImage)'}</span>
            </>
          )}
        </button>

        <p style={{ textAlign: 'center', fontSize: '0.72rem', color: 'var(--text-tertiary)', marginTop: '12px' }}>
          SHA-256 Verified Build • Runs with explicit user sandbox sandboxing
        </p>
      </div>
    </div>
  );
}
