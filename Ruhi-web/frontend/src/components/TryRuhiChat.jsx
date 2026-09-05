import React, { useState, useEffect, useRef } from 'react';
import { 
  Send, Sparkles, Trash2, Copy, Check, Terminal, AlertCircle, ArrowUpRight, Cpu, Mic, MicOff, Volume2 
} from 'lucide-react';
import { sendChatMessage, clearSessionContext, checkBackendHealth } from '../services/api';

export default function TryRuhiChat() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isThinking, setIsThinking] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(false);
  const [sessionId, setSessionId] = useState('');
  const [backendStatus, setBackendStatus] = useState({ online: true, model: 'gemini-2.5-flash' });
  const [errorMessage, setErrorMessage] = useState(null);
  const [copiedIndex, setCopiedIndex] = useState(null);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const recognitionRef = useRef(null);

  // Initialize Speech Recognition & Session ID
  useEffect(() => {
    let existingSession = sessionStorage.getItem('ruhi_session_id');
    if (!existingSession) {
      existingSession = 'ruhi_sess_' + Math.random().toString(36).substring(2, 11);
      sessionStorage.setItem('ruhi_session_id', existingSession);
    }
    setSessionId(existingSession);

    // Setup Web Speech API if supported
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      setSpeechSupported(true);
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onresult = (event) => {
        const transcript = Array.from(event.results)
          .map((result) => result[0])
          .map((result) => result.transcript)
          .join('');
        setInputMessage(transcript);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognition.onerror = (event) => {
        console.warn('Speech recognition status:', event.error);
        setIsListening(false);
      };

      recognitionRef.current = recognition;
    }

    // Check backend health
    checkBackendHealth()
      .then((res) => {
        setBackendStatus({
          online: res.status === 'healthy',
          model: res.model || 'gemini-2.5-flash',
          provider: res.llm_provider || 'Google Gemini',
        });
      })
      .catch(() => {
        setBackendStatus({ online: false, model: 'offline_fallback' });
      });
  }, []);

  // Auto-scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isThinking]);

  const suggestions = [
    { title: 'Explain something I\'m learning', query: 'Can you explain the core difference between monolithic AI models and personal AI systems in clear conceptual terms?' },
    { title: 'Help me plan my day', query: 'I have 3 high-priority engineering tasks and 2 meetings. Help me structure an optimal focus workflow for today.' },
    { title: 'Analyze this idea', query: 'Analyze the trade-offs of storing personal AI memories locally on-device versus encrypted in cloud vector stores.' },
    { title: 'Help me solve a problem', query: 'I need to design a clean Python abstraction that can swap between Gemini, Claude, and local Ollama models. Show me an example architecture.' },
    { title: 'Teach me something new', query: 'Teach me how autonomous AI agents maintain state and decide when to call external tools.' },
  ];

  const toggleVoiceInput = () => {
    if (!speechSupported) {
      const samplePrompts = [
        "Explain the difference between context and memory in personal AI.",
        "How does RUHI execute guarded desktop workflows?",
        "Help me structure a productive daily engineering workflow."
      ];
      const randomPrompt = samplePrompts[Math.floor(Math.random() * samplePrompts.length)];
      setInputMessage(randomPrompt);
      return;
    }
    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
    } else {
      try {
        recognitionRef.current?.start();
        setIsListening(true);
      } catch (err) {
        console.warn('Voice input start error:', err);
        setIsListening(false);
      }
    }
  };

  const handleSendMessage = async (textToSend) => {
    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
    }

    const text = (textToSend || inputMessage).trim();
    if (!text || isThinking) return;

    setErrorMessage(null);
    const userMsg = { role: 'user', content: text, timestamp: new Date().toISOString() };
    setMessages((prev) => [...prev, userMsg]);
    setInputMessage('');
    setIsThinking(true);

    try {
      const response = await sendChatMessage(text, sessionId);
      const assistantMsg = {
        role: 'assistant',
        content: response.message,
        timestamp: response.timestamp || new Date().toISOString(),
        model: response.model,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      setErrorMessage(err.message || 'Failed to communicate with RUHI backend.');
      const fallbackMsg = {
        role: 'assistant',
        content: `I encountered a communication issue (${err.message || 'Network error'}). Please check backend connection.`,
        timestamp: new Date().toISOString(),
        isError: true,
      };
      setMessages((prev) => [...prev, fallbackMsg]);
    } finally {
      setIsThinking(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleClearContext = async () => {
    if (messages.length === 0) return;
    try {
      await clearSessionContext(sessionId);
      setMessages([]);
      setErrorMessage(null);
    } catch (err) {
      console.error('Failed to reset session on server:', err);
      setMessages([]);
    }
  };

  const copyToClipboard = (code, idx) => {
    navigator.clipboard.writeText(code);
    setCopiedIndex(idx);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  // Helper to render markdown blocks & code snippets
  const renderMessageContent = (content) => {
    const codeBlockRegex = /```([a-zA-Z0-9_+-]*)\n([\s\S]*?)```/g;
    const parts = [];
    let lastIndex = 0;
    let match;
    let snippetId = 0;

    while ((match = codeBlockRegex.exec(content)) !== null) {
      // Text before code block
      if (match.index > lastIndex) {
        parts.push({
          type: 'text',
          content: content.slice(lastIndex, match.index),
        });
      }

      // Code block
      parts.push({
        type: 'code',
        language: match[1] || 'plaintext',
        code: match[2].trim(),
        id: snippetId++,
      });

      lastIndex = match.index + match[0].length;
    }

    // Remaining text
    if (lastIndex < content.length) {
      parts.push({
        type: 'text',
        content: content.slice(lastIndex),
      });
    }

    return (
      <div>
        {parts.map((part, pIdx) => {
          if (part.type === 'code') {
            return (
              <div key={pIdx} className="code-block-wrapper">
                <div className="code-block-header">
                  <span>{part.language.toUpperCase() || 'CODE'}</span>
                  <button 
                    onClick={() => copyToClipboard(part.code, `code_${pIdx}`)}
                    className="btn-code-copy"
                    aria-label="Copy code to clipboard"
                  >
                    {copiedIndex === `code_${pIdx}` ? (
                      <>
                        <Check size={12} color="#34d399" />
                        <span style={{ color: '#34d399' }}>Copied</span>
                      </>
                    ) : (
                      <>
                        <Copy size={12} />
                        <span>Copy</span>
                      </>
                    )}
                  </button>
                </div>
                <pre>
                  <code>{part.code}</code>
                </pre>
              </div>
            );
          }

          // Format paragraphs, bold, lists
          const paragraphs = part.content.split('\n\n');
          return paragraphs.map((para, paraIdx) => {
            if (para.startsWith('# ')) {
              return <h2 key={paraIdx} className="text-gradient-cyan">{para.replace('# ', '')}</h2>;
            }
            if (para.startsWith('## ')) {
              return <h3 key={paraIdx} style={{ color: 'var(--text-pure)' }}>{para.replace('## ', '')}</h3>;
            }
            if (para.startsWith('- ') || para.startsWith('* ')) {
              const items = para.split('\n').filter(i => i.trim());
              return (
                <ul key={paraIdx}>
                  {items.map((it, iIdx) => (
                    <li key={iIdx}>
                      {it.replace(/^[-*]\s+/, '').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')}
                    </li>
                  ))}
                </ul>
              );
            }

            // Regular paragraph with bold replacement
            const formattedPara = para.split(/(\*\*.*?\*\*)/g).map((chunk, cIdx) => {
              if (chunk.startsWith('**') && chunk.endsWith('**')) {
                return <strong key={cIdx}>{chunk.slice(2, -2)}</strong>;
              }
              return chunk;
            });

            return <p key={paraIdx}>{formattedPara}</p>;
          });
        })}
      </div>
    );
  };

  return (
    <section className="ruhi-section" id="try-ruhi">
      <div className="ruhi-container">
        <div className="section-header">
          <div className="section-badge">
            <Sparkles size={13} />
            <span>LIVE INTERACTIVE AI DEMO</span>
          </div>
          <h2 className="section-title">Try RUHI</h2>
          <p className="section-description">
            Experience RUHI's personal reasoning engine live. Maintain multi-turn context, test complex tasks, and witness calm, structured personal AI intelligence.
          </p>
        </div>

        {/* Signature Chat Console */}
        <div className="chat-console-wrapper">
          {/* Header */}
          <div className="chat-console-header">
            <div className="console-status-group">
              <div className="console-orb-mini">
                <img src="/ruhi-icon.svg" alt="RUHI Core" />
              </div>
              <div className="console-title-wrap">
                <span className="console-title">RUHI Personal AI</span>
                <span className="console-status-text">
                  <span className="console-status-dot" />
                  {isThinking ? 'RUHI is thinking...' : `Connected // ${backendStatus.model}`}
                </span>
              </div>
            </div>

            <div className="console-actions-group">
              <div className="context-counter-pill">
                <Cpu size={12} color="var(--cyan-primary)" />
                <span>Session Turns: {messages.length}</span>
              </div>

              {messages.length > 0 && (
                <button 
                  onClick={handleClearContext}
                  className="btn-console-clear"
                  aria-label="Clear active conversation session context"
                >
                  <Trash2 size={13} />
                  <span>Reset Context</span>
                </button>
              )}
            </div>
          </div>

          {/* Conversation Area */}
          <div className="chat-messages-container">
            {messages.length === 0 ? (
              <div className="chat-welcome-state">
                <img src="/ruhi-icon.svg" alt="RUHI Glyph" className="welcome-glyph" />
                <h3 className="welcome-heading">How can RUHI assist your workflow?</h3>
                <p className="welcome-desc">
                  Start a conversation below or pick a structured exploration scenario to observe RUHI's reasoning and session memory in action.
                </p>

                <div className="suggestions-deck">
                  {suggestions.map((s, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleSendMessage(s.query)}
                      className="suggestion-chip-btn"
                    >
                      <span>"{s.title}"</span>
                      <ArrowUpRight size={14} color="var(--cyan-primary)" />
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              messages.map((msg, idx) => (
                <div key={idx} className={`message-row ${msg.role === 'user' ? 'user' : 'ruhi'}`}>
                  <div className="message-avatar">
                    {msg.role === 'user' ? 'YOU' : <Sparkles size={16} />}
                  </div>
                  <div className="message-content-box">
                    {renderMessageContent(msg.content)}
                  </div>
                </div>
              ))
            )}

            {/* Calm Thinking State */}
            {isThinking && (
              <div className="ruhi-thinking-indicator">
                <div className="thinking-waves">
                  <div className="wave-bar" />
                  <div className="wave-bar" />
                  <div className="wave-bar" />
                </div>
                <span>RUHI is reasoning through your request...</span>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Composer */}
          <div className="chat-composer-area">
            {isListening && (
              <div className="voice-listening-banner">
                <span className="voice-pulse-circle" />
                <span>RUHI is listening to your speech... Speak clearly.</span>
              </div>
            )}

            <form className="composer-form" onSubmit={(e) => { e.preventDefault(); handleSendMessage(); }}>
              <input
                ref={inputRef}
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={isListening ? 'Listening to speech...' : 'Talk to RUHI...'}
                className="composer-input"
                disabled={isThinking}
                aria-label="Input prompt for RUHI"
              />

              <button
                type="button"
                onClick={toggleVoiceInput}
                className={`btn-composer-voice ${isListening ? 'listening' : ''}`}
                title={speechSupported ? (isListening ? 'Stop listening' : 'Start voice input') : 'Simulate voice speech prompt'}
                aria-label="Voice input toggle"
              >
                {isListening ? <MicOff size={16} /> : <Mic size={16} />}
              </button>

              <button
                type="submit"
                disabled={!inputMessage.trim() || isThinking}
                className="btn-composer-send"
                aria-label="Send message to RUHI"
              >
                <Send size={16} />
              </button>
            </form>

            <div className="composer-hint">
              Press Enter to send • Shift + Enter for newline • Voice input enabled
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
