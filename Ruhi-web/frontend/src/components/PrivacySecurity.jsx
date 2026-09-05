import React from 'react';
import { Lock, EyeOff, ShieldCheck, Key, RefreshCw, Trash2, Cpu } from 'lucide-react';

export default function PrivacySecurity() {
  const securityPillars = [
    {
      icon: <Key size={22} />,
      title: 'Server-Side Secret Isolation',
      desc: 'API keys and LLM tokens remain strictly isolated on the backend server. No secret keys or model credentials ever touch client-side browser code.',
    },
    {
      icon: <Lock size={22} />,
      title: 'Explicit Local Boundaries',
      desc: 'Installed RUHI runs within an isolated sandbox. Files, directories, and applications are accessible only after explicit, per-session user authorization.',
    },
    {
      icon: <Trash2 size={22} />,
      title: 'Transparent Memory Control',
      desc: 'You have full autonomy to inspect active session context or permanently purge memory threads at any moment with a single click.',
    },
    {
      icon: <RefreshCw size={22} />,
      title: 'Instant Permission Revocation',
      desc: 'Revoke tool access, file watchers, or automation permissions at runtime without needing to reconfigure or restart the application.',
    },
    {
      icon: <EyeOff size={22} />,
      title: 'Zero Background Data Mining',
      desc: 'RUHI does not harvest your personal documents, keystrokes, or background screen data. All AI queries are initiated directly by your explicit intent.',
    },
    {
      icon: <ShieldCheck size={22} />,
      title: 'Auditable Action Logs',
      desc: 'Every file read, tool invocation, and terminal execution produces an auditable log entry for complete transparency and peace of mind.',
    },
  ];

  return (
    <section className="ruhi-section" id="privacy">
      <div className="ruhi-container">
        <div className="section-header">
          <div className="section-badge">
            <Lock size={13} />
            <span>PRIVACY & SECURITY POSTURE</span>
          </div>
          <h2 className="section-title">Your Data. Your Control.</h2>
          <p className="section-description">
            A personal AI system is only as good as the trust you place in it. RUHI is engineered with zero-compromise security boundaries, transparent data controls, and absolute user authority.
          </p>
        </div>

        <div className="privacy-grid">
          {securityPillars.map((pillar, idx) => (
            <div key={idx} className="privacy-card">
              <div className="privacy-card-icon">
                {pillar.icon}
              </div>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '8px', color: 'var(--text-pure)' }}>
                {pillar.title}
              </h3>
              <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                {pillar.desc}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
