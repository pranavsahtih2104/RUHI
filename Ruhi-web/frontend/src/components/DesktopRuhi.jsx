import React, { useState } from 'react';
import { 
  Monitor, Folder, Terminal, Mic, ShieldCheck, CheckCircle2, Lock, 
  ArrowRight, Download, Play, Cpu, AlertTriangle, FileText 
} from 'lucide-react';

export default function DesktopRuhi({ onOpenInstallModal }) {
  const [selectedWorkflow, setSelectedWorkflow] = useState(0);
  const [permissions, setPermissions] = useState({
    files: true,
    apps: true,
    mic: false,
    automation: true,
  });

  const workflows = [
    {
      title: 'Project Launch & Context Alignment',
      prompt: 'User: "Open the RUHI project I was working on yesterday in VS Code."',
      steps: [
        '1. Resolves natural language intent and queries local session memory.',
        '2. Matches "RUHI project" to ~/Documents/RUHI.',
        '3. Verifies authorization for Application Launch tool.',
        '4. Launches VS Code with ~/Documents/RUHI workspace focused.',
      ],
      terminalOutput: '$ ruhi-agent exec app.launch --app "Visual Studio Code" --path "~/Documents/RUHI"\n> Process spawned [PID: 48192]\n> RUHI Context loaded: 14 files indexed',
    },
    {
      title: 'Authorized Local File Search',
      prompt: 'User: "Find the research paper on neural orchestration I downloaded last week."',
      steps: [
        '1. Parses semantic query into search tokens: ["research paper", "neural orchestration"].',
        '2. Scans authorized ~/Downloads directory without cloud upload.',
        '3. Indexes metadata and locates "Neural_Orchestrator_2026.pdf".',
        '4. Displays interactive preview with one-click open.',
      ],
      terminalOutput: '$ ruhi-agent file.search --dir "~/Downloads" --query "neural orchestration"\n> Found 1 match: ~/Downloads/Neural_Orchestrator_2026.pdf (1.4 MB)\n> Safety check: Verified SHA-256 integrity.',
    },
    {
      title: 'Multi-Step Build & Test Automation',
      prompt: 'User: "Run the test suite on the backend and notify me when completed."',
      steps: [
        '1. Navigates to authorized project directory.',
        '2. Executes pytest within isolated virtual environment.',
        '3. Monitors stderr/stdout in background without freezing UI.',
        '4. Delivers concise summary notification upon completion.',
      ],
      terminalOutput: '$ ruhi-agent task.run --cmd "pytest tests/ --verbose"\n> Running 18 tests...\n> 18 passed in 1.42s [100%]\n> Notification delivered.',
    },
  ];

  const currentWorkflow = workflows[selectedWorkflow];

  const togglePermission = (key) => {
    setPermissions((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <section className="ruhi-section" id="desktop-ruhi">
      <div className="ruhi-container">
        <div className="section-header">
          <div className="section-badge">
            <Monitor size={13} />
            <span>DESKTOP ECOSYSTEM</span>
          </div>
          <h2 className="section-title">
            RUHI Becomes More Powerful <br />
            <span className="text-gradient-cyan">When Installed.</span>
          </h2>
          <p className="section-description">
            The web version is only the beginning. Installed RUHI operates as an intelligent local companion with access to your files, desktop applications, and automated workflows — always under your explicit authorization.
          </p>
        </div>

        {/* Interactive Desktop Simulation Card */}
        <div className="desktop-hero-card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
            <div>
              <span className="brand-tag">DESKTOP SIMULATION</span>
              <h3 style={{ fontSize: '1.4rem', fontWeight: 800, marginTop: '6px' }}>
                Simulated Local Execution
              </h3>
            </div>
            <button 
              onClick={onOpenInstallModal}
              className="btn-primary"
              style={{ padding: '10px 22px', fontSize: '0.85rem' }}
            >
              <Download size={15} />
              <span>Install RUHI Desktop</span>
            </button>
          </div>

          <div className="desktop-sim-grid">
            {/* Left: Workflow Selection */}
            <div className="desktop-action-selector">
              {workflows.map((wf, idx) => (
                <button
                  key={idx}
                  onClick={() => setSelectedWorkflow(idx)}
                  className={`desktop-action-btn ${selectedWorkflow === idx ? 'active' : ''}`}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
                    <Play size={14} color={selectedWorkflow === idx ? 'var(--cyan-primary)' : 'var(--text-tertiary)'} />
                    <strong style={{ fontSize: '0.95rem' }}>{wf.title}</strong>
                  </div>
                  <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', fontStyle: 'italic' }}>
                    {wf.prompt}
                  </div>
                </button>
              ))}
            </div>

            {/* Right: Terminal Telemetry & Pipeline */}
            <div className="desktop-terminal-preview">
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '8px' }}>
                <span style={{ color: 'var(--text-tertiary)' }}>ruhi-desktop-daemon // authorized</span>
                <span style={{ color: '#34d399', fontSize: '0.75rem' }}>SANDBOXED</span>
              </div>
              <div style={{ whiteSpace: 'pre-wrap', lineHeight: 1.6, color: '#38bdf8' }}>
                {currentWorkflow.terminalOutput}
              </div>
              <div style={{ marginTop: '12px', borderTop: '1px solid var(--border-subtle)', paddingTop: '10px' }}>
                <strong style={{ color: 'var(--text-pure)', fontSize: '0.8rem' }}>EXECUTION SEQUENCE:</strong>
                <ul style={{ listStyle: 'none', marginTop: '6px', display: 'flex', flexDirection: 'column', gap: '4px', fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                  {currentWorkflow.steps.map((s, i) => (
                    <li key={i}>{s}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Permission Safety Dashboard */}
        <div className="perm-engine-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
            <ShieldCheck size={22} color="#34d399" />
            <h3 style={{ fontSize: '1.25rem', fontWeight: 700 }}>RUHI Permission Engine</h3>
          </div>
          <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)' }}>
            RUHI never operates with unrestricted system control. Every capability requires explicit, transparent, and revocable user consent.
          </p>

          <div className="perm-toggles-grid">
            {/* File Access */}
            <div className="perm-toggle-item">
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                  <Folder size={16} color="var(--cyan-primary)" />
                  <strong style={{ fontSize: '0.9rem' }}>Local Files</strong>
                </div>
                <p style={{ fontSize: '0.76rem', color: 'var(--text-secondary)' }}>
                  Search and read user-authorized workspaces.
                </p>
              </div>
              <button 
                onClick={() => togglePermission('files')}
                className={`perm-toggle-btn ${permissions.files ? 'allowed' : 'blocked'}`}
              >
                {permissions.files ? 'Allowed' : 'Don\'t Allow'}
              </button>
            </div>

            {/* Applications */}
            <div className="perm-toggle-item">
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                  <Terminal size={16} color="var(--cyan-primary)" />
                  <strong style={{ fontSize: '0.9rem' }}>Applications</strong>
                </div>
                <p style={{ fontSize: '0.76rem', color: 'var(--text-secondary)' }}>
                  Launch authorized developer and system apps.
                </p>
              </div>
              <button 
                onClick={() => togglePermission('apps')}
                className={`perm-toggle-btn ${permissions.apps ? 'allowed' : 'blocked'}`}
              >
                {permissions.apps ? 'Allowed' : 'Don\'t Allow'}
              </button>
            </div>

            {/* Microphone */}
            <div className="perm-toggle-item">
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                  <Mic size={16} color="var(--cyan-primary)" />
                  <strong style={{ fontSize: '0.9rem' }}>Microphone</strong>
                </div>
                <p style={{ fontSize: '0.76rem', color: 'var(--text-secondary)' }}>
                  Hands-free natural speech interaction.
                </p>
              </div>
              <button 
                onClick={() => togglePermission('mic')}
                className={`perm-toggle-btn ${permissions.mic ? 'allowed' : 'blocked'}`}
              >
                {permissions.mic ? 'Allowed' : 'Don\'t Allow'}
              </button>
            </div>

            {/* Automation */}
            <div className="perm-toggle-item">
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                  <Cpu size={16} color="var(--cyan-primary)" />
                  <strong style={{ fontSize: '0.9rem' }}>Automation</strong>
                </div>
                <p style={{ fontSize: '0.76rem', color: 'var(--text-secondary)' }}>
                  Run build scripts, tests, and task pipelines.
                </p>
              </div>
              <button 
                onClick={() => togglePermission('automation')}
                className={`perm-toggle-btn ${permissions.automation ? 'allowed' : 'blocked'}`}
              >
                {permissions.automation ? 'Allowed' : 'Don\'t Allow'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
