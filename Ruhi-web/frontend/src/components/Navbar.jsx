import React, { useState, useEffect } from 'react';
import { Sparkles, Download, Menu, X, ArrowUpRight } from 'lucide-react';

export default function Navbar({ onOpenInstallModal, onNavigateToChat }) {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 30);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navLinks = [
    { label: 'Vision', href: '#what-is-ruhi' },
    { label: 'Why RUHI', href: '#why-ruhi' },
    { label: 'Capabilities', href: '#capabilities' },
    { label: 'Architecture', href: '#how-it-works' },
    { label: 'Desktop AI', href: '#desktop-ruhi' },
    { label: 'Privacy', href: '#privacy' },
  ];

  return (
    <nav className={`ruhi-navbar ${scrolled ? 'scrolled' : ''}`}>
      <div className="ruhi-container nav-container">
        {/* Brand Logo & Tag */}
        <a href="#" className="brand-link">
          <img src="/ruhi-icon.svg" alt="RUHI Emblem" className="brand-icon" />
          <span className="brand-text">RUHI</span>
          <span className="brand-tag">v0.1.0</span>
        </a>

        {/* Desktop Navigation Links */}
        <ul className="nav-links">
          {navLinks.map((link) => (
            <li key={link.label}>
              <a href={link.href} className="nav-item">
                {link.label}
              </a>
            </li>
          ))}
        </ul>

        {/* Action CTAs */}
        <div className="nav-actions">
          <button 
            onClick={onNavigateToChat}
            className="btn-nav-try"
            aria-label="Experience Web RUHI"
          >
            <Sparkles size={14} className="text-gradient-cyan" />
            <span>Try RUHI</span>
          </button>

          <button 
            onClick={onOpenInstallModal}
            className="btn-nav-install"
            aria-label="Install Desktop RUHI"
          >
            <Download size={14} />
            <span>Install RUHI</span>
          </button>

          <button 
            className="mobile-menu-btn"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle Navigation Menu"
          >
            {mobileMenuOpen ? <X size={22} /> : <Menu size={22} />}
          </button>
        </div>
      </div>

      {/* Mobile Menu Dropdown */}
      {mobileMenuOpen && (
        <div className="mobile-menu-dropdown glass-panel" style={{
          position: 'absolute',
          top: '76px',
          left: '16px',
          right: '16px',
          padding: '24px',
          display: 'flex',
          flexDirection: 'column',
          gap: '16px',
          zIndex: 99,
        }}>
          {navLinks.map((link) => (
            <a
              key={link.label}
              href={link.href}
              onClick={() => setMobileMenuOpen(false)}
              style={{
                color: 'var(--text-primary)',
                fontSize: '1rem',
                fontWeight: 600,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}
            >
              <span>{link.label}</span>
              <ArrowUpRight size={16} color="var(--cyan-primary)" />
            </a>
          ))}
          <div style={{ display: 'flex', gap: '12px', marginTop: '12px' }}>
            <button 
              onClick={() => { setMobileMenuOpen(false); onNavigateToChat(); }}
              className="btn-primary" 
              style={{ flex: 1, padding: '10px 16px', fontSize: '0.85rem' }}
            >
              Try RUHI
            </button>
            <button 
              onClick={() => { setMobileMenuOpen(false); onOpenInstallModal(); }}
              className="btn-secondary" 
              style={{ flex: 1, padding: '10px 16px', fontSize: '0.85rem' }}
            >
              Install
            </button>
          </div>
        </div>
      )}
    </nav>
  );
}
