import React, { useState } from 'react';
import { 
  User, Sparkles, MessageSquare, Compass, Database, 
  Brain, Wrench, Play, CheckCircle2, GitBranch, Terminal 
} from 'lucide-react';

export default function HowItWorks() {
  const [activeStep, setActiveStep] = useState(0);

  const pipelineSteps = [
    {
      label: 'YOU',
      title: '01. User Intent',
      icon: <User size={18} />,
      desc: 'You communicate a natural language goal, query, or complex task.',
      simulation: 'User: "Analyze my project notes and prepare a deployment plan."',
    },
    {
      label: 'RUHI',
      title: '02. System Gateway',
      icon: <Sparkles size={18} />,
      desc: 'RUHI ingests the prompt through its decoupled AI orchestrator.',
      simulation: 'Gateway: Ingesting payload into active session context...',
    },
    {
      label: 'UNDERSTAND',
      title: '03. Semantic Perception',
      icon: <MessageSquare size={18} />,
      desc: 'Extracts core intent, constraints, entities, and implied sub-tasks.',
      simulation: 'Intent: [Project Analysis] + [Deployment Plan Generation]',
    },
    {
      label: 'CONTEXT',
      title: '04. Session Context',
      icon: <Compass size={18} />,
      desc: 'Aligns the request with active conversational history and current working state.',
      simulation: 'Context: Referencing active session thread #8f12a9',
    },
    {
      label: 'MEMORY',
      title: '05. Knowledge Retrieval',
      icon: <Database size={18} />,
      desc: 'Queries stored personal guidelines, preferences, and workspace knowledge.',
      simulation: 'Memory Query: Fetching user architecture preferences...',
    },
    {
      label: 'REASON',
      title: '06. Cognitive Planning',
      icon: <Brain size={18} />,
      desc: 'Deconstructs the objective into a sequence of verified logic gates.',
      simulation: 'Planner: Generating 3-phase execution plan & validating risks...',
    },
    {
      label: 'TOOLS',
      title: '07. Tool Selection',
      icon: <Wrench size={18} />,
      desc: 'Evaluates if external capabilities (search, file reading, code generation) are needed.',
      simulation: 'Tool Evaluator: Web Retrieval (Optional), Local Code Gen (Active)',
    },
    {
      label: 'ACTION',
      title: '08. Guarded Execution',
      icon: <Play size={18} />,
      desc: 'Executes verified operations with user permission boundaries in place.',
      simulation: 'Execution: Formatting structured response and code artifacts...',
    },
    {
      label: 'RESULT',
      title: '09. Actionable Output',
      icon: <CheckCircle2 size={18} />,
      desc: 'Returns a clear, high-fidelity response, actionable plan, or executed workflow.',
      simulation: 'Outcome: Structured deployment guide ready for user execution.',
    },
  ];

  const current = pipelineSteps[activeStep];

  return (
    <section className="ruhi-section" id="how-it-works">
      <div className="ruhi-container">
        <div className="section-header">
          <div className="section-badge">
            <GitBranch size={13} />
            <span>INTERACTIVE EXECUTION PIPELINE</span>
          </div>
          <h2 className="section-title">How RUHI Works</h2>
          <p className="section-description">
            RUHI processes requests through an end-to-end cognitive pipeline. Click or hover any stage to inspect how intelligence transforms into action.
          </p>
        </div>

        <div className="pipeline-container">
          {/* Stepper Navigation */}
          <div className="pipeline-stepper">
            {pipelineSteps.map((step, idx) => {
              const isActive = activeStep === idx;
              return (
                <button
                  key={step.label}
                  onClick={() => setActiveStep(idx)}
                  className={`pipe-node-btn ${isActive ? 'active' : ''}`}
                  aria-label={`Inspect step ${step.title}`}
                >
                  <div className="pipe-icon-circle">
                    {step.icon}
                  </div>
                  <span className="pipe-node-label">{step.label}</span>
                </button>
              );
            })}
          </div>

          {/* Step Detail Card */}
          <div className="pipeline-detail-card">
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px', color: 'var(--cyan-primary)' }}>
                <Terminal size={16} />
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', textTransform: 'uppercase' }}>
                  STAGE {activeStep + 1} OF 9
                </span>
              </div>
              <h3 className="pipe-detail-title">{current.title}</h3>
              <p className="pipe-detail-desc">{current.desc}</p>

              <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
                <button
                  onClick={() => setActiveStep((prev) => (prev > 0 ? prev - 1 : pipelineSteps.length - 1))}
                  className="btn-secondary"
                  style={{ padding: '8px 18px', fontSize: '0.8rem' }}
                >
                  Previous Stage
                </button>
                <button
                  onClick={() => setActiveStep((prev) => (prev < pipelineSteps.length - 1 ? prev + 1 : 0))}
                  className="btn-primary"
                  style={{ padding: '8px 18px', fontSize: '0.8rem' }}
                >
                  Next Stage
                </button>
              </div>
            </div>

            {/* Simulated Terminal Telemetry */}
            <div className="pipe-simulation-box">
              <div style={{ color: 'var(--text-tertiary)', marginBottom: '8px', fontSize: '0.75rem' }}>
                // RUHI COGNITIVE TELEMETRY
              </div>
              <div style={{ whiteSpace: 'pre-wrap', lineHeight: 1.6 }}>
                &gt; {current.simulation}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
