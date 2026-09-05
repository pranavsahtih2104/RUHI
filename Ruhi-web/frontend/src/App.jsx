import React, { useState } from 'react';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import WhatIsRuhi from './components/WhatIsRuhi';
import WhyRuhi from './components/WhyRuhi';
import Capabilities from './components/Capabilities';
import HowItWorks from './components/HowItWorks';
import Personality from './components/Personality';
import TryRuhiChat from './components/TryRuhiChat';
import MemoryConcept from './components/MemoryConcept';
import DesktopRuhi from './components/DesktopRuhi';
import ComparisonMatrix from './components/ComparisonMatrix';
import PrivacySecurity from './components/PrivacySecurity';
import InstallModal from './components/InstallModal';
import Footer from './components/Footer';

import './styles/index.css';
import './styles/components.css';
import './styles/chat.css';

export default function App() {
  const [isInstallModalOpen, setIsInstallModalOpen] = useState(false);

  const scrollToSection = (id) => {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="ruhi-app-root">
      {/* 1. Global Navigation Bar */}
      <Navbar
        onOpenInstallModal={() => setIsInstallModalOpen(true)}
        onNavigateToChat={() => scrollToSection('try-ruhi')}
      />

      <main>
        {/* 2. Hero Stage with Intelligent Neural Orb */}
        <Hero
          onExploreClick={() => scrollToSection('what-is-ruhi')}
          onTryClick={() => scrollToSection('try-ruhi')}
        />

        {/* 3. Introduction Section: "What is RUHI?" */}
        <WhatIsRuhi />

        {/* 4. "Why RUHI?" Tool vs. Personal System Comparison */}
        <WhyRuhi />

        {/* 5. Capability Matrix (Categorized & Status Badged) */}
        <Capabilities />

        {/* 6. 9-Stage Cognitive Architecture Pipeline */}
        <HowItWorks />

        {/* 7. "Meet RUHI" Ethos & Demeanor */}
        <Personality />

        {/* 8. Live Interactive "Try RUHI" Console */}
        <TryRuhiChat />

        {/* 9. Continuity & Memory System Architecture */}
        <MemoryConcept />

        {/* 10. Desktop RUHI Ecosystem & Permission Engine */}
        <DesktopRuhi
          onOpenInstallModal={() => setIsInstallModalOpen(true)}
        />

        {/* 11. Transparent Comparison: Web vs Desktop */}
        <ComparisonMatrix />

        {/* 12. Privacy & Security: "Your Data. Your Control." */}
        <PrivacySecurity />
      </main>

      {/* 13. Global Footer */}
      <Footer
        onOpenInstallModal={() => setIsInstallModalOpen(true)}
      />

      {/* 14. Installation Modal */}
      <InstallModal
        isOpen={isInstallModalOpen}
        onClose={() => setIsInstallModalOpen(false)}
      />
    </div>
  );
}
