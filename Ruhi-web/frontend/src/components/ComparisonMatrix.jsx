import React from 'react';
import { Check, X, Clock, Sliders, Shield } from 'lucide-react';

export default function ComparisonMatrix() {
  const rows = [
    { capability: 'Conversational AI & Reasoning', web: 'yes', desktop: 'yes' },
    { capability: 'Active Multi-Turn Session Context', web: 'yes', desktop: 'yes' },
    { capability: 'Persistent Long-Term Memory', web: 'planned', desktop: 'planned_desktop' },
    { capability: 'Local Files & Directory Search', web: 'limited', desktop: 'yes_permission' },
    { capability: 'Desktop Application Launching', web: 'no', desktop: 'yes_permission' },
    { capability: 'System-Level Task Automation', web: 'no', desktop: 'yes_permission' },
    { capability: 'Voice & Speech Interaction', web: 'planned', desktop: 'planned' },
    { capability: 'Local Hardware & GPU Model Weights', web: 'no', desktop: 'yes_permission' },
    { capability: 'Offline Operation Capability', web: 'no', desktop: 'planned' },
  ];

  const renderBadge = (type) => {
    switch (type) {
      case 'yes':
        return (
          <span style={{ color: '#34d399', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Check size={16} />
            <span>Supported</span>
          </span>
        );
      case 'yes_permission':
        return (
          <span style={{ color: 'var(--cyan-primary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Check size={16} />
            <span>Authorized Only</span>
          </span>
        );
      case 'limited':
        return (
          <span style={{ color: '#fbbf24', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Sliders size={16} />
            <span>Manual Input Only</span>
          </span>
        );
      case 'planned':
      case 'planned_desktop':
        return (
          <span style={{ color: 'var(--text-tertiary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Clock size={16} />
            <span>Planned</span>
          </span>
        );
      case 'no':
        return (
          <span style={{ color: '#f87171', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <X size={16} />
            <span>Browser Sandbox</span>
          </span>
        );
      default:
        return null;
    }
  };

  return (
    <section className="ruhi-section" id="comparison-matrix">
      <div className="ruhi-container">
        <div className="section-header">
          <div className="section-badge">
            <Shield size={13} />
            <span>TRANSPARENT FEATURE COMPARISON</span>
          </div>
          <h2 className="section-title">Web RUHI vs Installed RUHI</h2>
          <p className="section-description">
            We believe in honest technology. Here is the exact distinction between what runs inside your web browser today versus the capabilities unlocked with RUHI Desktop.
          </p>
        </div>

        <div className="matrix-table-wrapper">
          <table className="matrix-table">
            <thead>
              <tr>
                <th style={{ width: '46%' }}>System Capability</th>
                <th style={{ width: '27%' }}>Web RUHI (Online)</th>
                <th style={{ width: '27%' }}>Installed RUHI (Desktop)</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row, idx) => (
                <tr key={idx}>
                  <td style={{ fontWeight: 600, color: 'var(--text-pure)' }}>
                    {row.capability}
                  </td>
                  <td>{renderBadge(row.web)}</td>
                  <td>{renderBadge(row.desktop)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
