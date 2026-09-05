import React, { useState } from 'react';
import { 
  MessageSquare, Database, BookOpen, BrainCircuit, Play, PenTool, 
  Check, Clock, Monitor, Layers 
} from 'lucide-react';

export default function Capabilities() {
  const [activeCategory, setActiveCategory] = useState('all');

  const categories = [
    { id: 'all', label: 'All Capabilities' },
    { id: 'understand', label: 'Understand' },
    { id: 'remember', label: 'Remember' },
    { id: 'know', label: 'Know' },
    { id: 'think', label: 'Think' },
    { id: 'act', label: 'Act' },
    { id: 'create', label: 'Create' },
  ];

  const capabilityCards = [
    {
      category: 'understand',
      title: 'Understand',
      icon: <MessageSquare size={20} />,
      desc: 'Deep conversational perception that captures nuanced constraints, tone, and multi-turn user intent.',
      items: [
        { name: 'Natural Conversation', status: 'available_now' },
        { name: 'Intent Extraction & Synthesis', status: 'available_now' },
        { name: 'Active Context Awareness', status: 'available_now' },
        { name: 'Complex Multi-Turn Requests', status: 'available_now' },
      ]
    },
    {
      category: 'remember',
      title: 'Remember',
      icon: <Database size={20} />,
      desc: 'Seamless continuity across dialogue turns, evolving into long-term personal context.',
      items: [
        { name: 'Active Session History', status: 'available_now' },
        { name: 'User Preferences & Guidelines', status: 'coming_soon' },
        { name: 'Cross-Session Long-Term Memory', status: 'coming_soon' },
        { name: 'Inspectable Memory Vault', status: 'coming_soon' },
      ]
    },
    {
      category: 'know',
      title: 'Know',
      icon: <BookOpen size={20} />,
      desc: 'Grounded intelligence referencing live documentation, uploaded data, and local files.',
      items: [
        { name: 'General AI Knowledge & Web Intel', status: 'available_now' },
        { name: 'User-Supplied Text & Notes', status: 'available_now' },
        { name: 'Local Hard Drive Indexing', status: 'desktop_only' },
        { name: 'Local File Semantic Search', status: 'desktop_only' },
      ]
    },
    {
      category: 'think',
      title: 'Think',
      icon: <BrainCircuit size={20} />,
      desc: 'Decomposing complex goals into structured logic, tool selection strategies, and architectural blueprints.',
      items: [
        { name: 'Step-by-Step Task Breakdown', status: 'available_now' },
        { name: 'Strategic Project Planning', status: 'available_now' },
        { name: 'Tool Selection Reasoning', status: 'available_now' },
        { name: 'Iterative Self-Critique', status: 'coming_soon' },
      ]
    },
    {
      category: 'act',
      title: 'Act',
      icon: <Play size={20} />,
      desc: 'Bridging thoughts into concrete actions with strict user approval and safety boundaries.',
      items: [
        { name: 'Structured Action Plans', status: 'available_now' },
        { name: 'Desktop App Automation', status: 'desktop_only' },
        { name: 'Local Shell Execution', status: 'desktop_only' },
        { name: 'Permissioned File Operations', status: 'desktop_only' },
      ]
    },
    {
      category: 'create',
      title: 'Create',
      icon: <PenTool size={20} />,
      desc: 'Generating clean software code, analytical documents, workflows, and creative ideas.',
      items: [
        { name: 'Production Code & Refactoring', status: 'available_now' },
        { name: 'Analytical Synthesis & Writing', status: 'available_now' },
        { name: 'Multi-File Local Scaffolding', status: 'desktop_only' },
        { name: 'Automated Asset Pipelines', status: 'desktop_only' },
      ]
    },
  ];

  const filteredCards = activeCategory === 'all' 
    ? capabilityCards 
    : capabilityCards.filter(c => c.category === activeCategory);

  const getStatusBadge = (status) => {
    switch (status) {
      case 'available_now':
        return (
          <span className="status-pill status-available">
            <Check size={10} />
            <span>Available Now</span>
          </span>
        );
      case 'coming_soon':
        return (
          <span className="status-pill status-coming-soon">
            <Clock size={10} />
            <span>Coming Soon</span>
          </span>
        );
      case 'desktop_only':
        return (
          <span className="status-pill status-desktop-only">
            <Monitor size={10} />
            <span>Desktop Only</span>
          </span>
        );
      default:
        return null;
    }
  };

  return (
    <section className="ruhi-section" id="capabilities">
      <div className="ruhi-container">
        <div className="section-header">
          <div className="section-badge">
            <Layers size={13} />
            <span>TRANSPARENT SYSTEM CAPABILITIES</span>
          </div>
          <h2 className="section-title">What Can RUHI Do?</h2>
          <p className="section-description">
            Explore RUHI's capabilities across perception, memory, reasoning, and execution. We are fully transparent about what is available now in the web experience versus what is unlocked on your desktop.
          </p>
        </div>

        {/* Filter Pills */}
        <div className="capabilities-filters">
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setActiveCategory(cat.id)}
              className={`filter-pill ${activeCategory === cat.id ? 'active' : ''}`}
            >
              {cat.label}
            </button>
          ))}
        </div>

        {/* Capabilities Grid */}
        <div className="capabilities-grid">
          {filteredCards.map((card) => (
            <div key={card.category} className="capability-card">
              <div className="cap-icon-box">
                {card.icon}
              </div>

              <h3 className="cap-card-title">{card.title}</h3>
              <p className="cap-card-desc">{card.desc}</p>

              <ul className="cap-features-list">
                {card.items.map((item, idx) => (
                  <li key={idx} className="cap-feature-row">
                    <span className="cap-feature-name">{item.name}</span>
                    {getStatusBadge(item.status)}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
