import React from 'react';
import { Compass, Shield, Feather, Sparkles, Sliders } from 'lucide-react';

export default function Personality() {
  const traits = [
    {
      icon: <Feather size={22} />,
      title: 'Calm & Precise',
      text: 'RUHI avoids artificial hype, exaggerated emojis, and sycophantic praise. It speaks with steady clarity, grounding every answer in logic.',
    },
    {
      icon: <Sparkles size={22} />,
      title: 'Deeply Analytical',
      text: 'When presented with complex challenges, RUHI conducts systematic breakdowns, examines alternative approaches, and plans rigorously.',
    },
    {
      icon: <Shield size={22} />,
      title: 'Respectful & Honest',
      text: 'RUHI never fabricates phantom capabilities. It is transparent about what it can execute in the web browser versus what requires desktop permissions.',
    },
    {
      icon: <Sliders size={22} />,
      title: 'Context-Adaptive',
      text: 'Concise when you need a swift reference; comprehensive and nuanced when co-architecting systems or exploring foundational concepts.',
    },
  ];

  return (
    <section className="ruhi-section" id="personality">
      <div className="ruhi-container">
        <div className="section-header">
          <div className="section-badge">
            <Compass size={13} />
            <span>ETHOS & DEMEANOR</span>
          </div>
          <h2 className="section-title">Meet RUHI</h2>
          <p className="section-description">
            RUHI is engineered as an intelligent personal computing companion. Not a cartoon chatbot, not a synthetic human, but a disciplined cognitive partner.
          </p>
        </div>

        <div className="personality-grid">
          {traits.map((trait, idx) => (
            <div key={idx} className="personality-card">
              <div className="personality-icon">
                {trait.icon}
              </div>
              <h3 className="personality-title">{trait.title}</h3>
              <p className="personality-text">{trait.text}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
