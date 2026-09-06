import React, { useState, useEffect, useRef } from 'react';
import { 
  Send, Sparkles, Trash2, Copy, Check, AlertCircle, ArrowUpRight, Cpu, 
  Mic, MicOff, RefreshCw, RotateCcw, MessageSquare, Brain, History, ChevronLeft, ChevronRight, ShieldCheck
} from 'lucide-react';
import { 
  sendChatMessage, 
  sendStreamingChatMessage, 
  clearSessionContext, 
  checkBackendHealth,
  fetchConversations,
  createConversation,
  fetchConversationDetail,
  renameConversation,
  deleteConversation,
  fetchMemories,
} from '../services/api';
import { useSpeechRecognition } from '../hooks/useSpeechRecognition';
import VoiceStatusBanner from './VoiceStatusBanner';
import ChatSidebar from './ChatSidebar';
import MemoryModal from './MemoryModal';

export default function TryRuhiChat() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isThinking, setIsThinking] = useState(false);
  const [streamingContent, setStreamingContent] = useState('');
  const [activeConversationId, setActiveConversationId] = useState('');
  const [conversations, setConversations] = useState([]);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isMemoryModalOpen, setIsMemoryModalOpen] = useState(false);
  const [memoryCount, setMemoryCount] = useState(0);
  const [backendHealth, setBackendHealth] = useState({ online: false, configured: false, database_connected: false });
  const [errorMessage, setErrorMessage] = useState(null);
  const [copiedIndex, setCopiedIndex] = useState(null);
  const [latestMemoryEvent, setLatestMemoryEvent] = useState(null);

  const messagesContainerRef = useRef(null);
  const inputRef = useRef(null);
  const isInitialMountRef = useRef(true);

  // Hook up robust speech recognition
  const handleFinalVoiceTranscript = (finalText) => {
    setInputMessage((prev) => {
      const trimmed = prev.trim();
      return trimmed ? `${trimmed} ${finalText}` : finalText;
    });
    inputRef.current?.focus();
  };

  const handleInterimVoiceTranscript = (interimText) => {
    // Interim transcript updates
  };

  const {
    voiceState,
    isListening,
    errorMessage: voiceError,
    interimTranscript,
    startListening,
    stopListening,
    resetVoiceState,
  } = useSpeechRecognition({
    onTranscript: handleInterimVoiceTranscript,
    onFinalTranscript: handleFinalVoiceTranscript,
  });

  // Load conversations & memory count on mount
  const refreshConversations = async () => {
    try {
      const list = await fetchConversations();
      setConversations(list || []);
      return list;
    } catch (err) {
      console.error('Failed to load conversations:', err);
      return [];
    }
  };

  const refreshMemoryCount = async () => {
    try {
      const res = await fetchMemories({ active: true, limit: 1 });
      setMemoryCount(res.total || 0);
    } catch (err) {
      console.error('Failed to load memory count:', err);
    }
  };

  useEffect(() => {
    const initSessionAndData = async () => {
      const list = await refreshConversations();
      await refreshMemoryCount();

      let savedId = sessionStorage.getItem('ruhi_active_conv_id');
      if (savedId && list.some(c => c.id === savedId)) {
        await handleSelectConversation(savedId);
      } else if (list.length > 0) {
        await handleSelectConversation(list[0].id);
      } else {
        // Create initial persistent conversation
        try {
          const newConv = await createConversation("New Conversation");
          setActiveConversationId(newConv.id);
          sessionStorage.setItem('ruhi_active_conv_id', newConv.id);
          setConversations([newConv]);
        } catch (e) {
          const fallbackId = 'conv_' + Math.random().toString(36).substring(2, 10);
          setActiveConversationId(fallbackId);
        }
      }
    };

    initSessionAndData();

    // Initial and periodic backend health check
    const performHealthCheck = () => {
      checkBackendHealth()
        .then((res) => {
          setBackendHealth({
            online: res.status === 'healthy' || res.status === 'degraded',
            configured: res.configured_api_key,
            database_connected: res.database_connected,
          });
        })
        .catch(() => {
          setBackendHealth({ online: false, configured: false, database_connected: false });
        });
    };

    performHealthCheck();
    const intervalId = setInterval(performHealthCheck, 30000);
    return () => clearInterval(intervalId);
  }, []);

  // Auto-scroll to bottom of messages inside chat container during active conversation
  useEffect(() => {
    if (isInitialMountRef.current) {
      isInitialMountRef.current = false;
      return;
    }

    if (messages.length > 0 || streamingContent || isThinking) {
      if (messagesContainerRef.current) {
        messagesContainerRef.current.scrollTo({
          top: messagesContainerRef.current.scrollHeight,
          behavior: 'smooth'
        });
      }
    }
  }, [messages, streamingContent, isThinking]);

  const handleSelectConversation = async (convId) => {
    setActiveConversationId(convId);
    sessionStorage.setItem('ruhi_active_conv_id', convId);
    setStreamingContent('');
    setErrorMessage(null);
    setLatestMemoryEvent(null);

    try {
      const detail = await fetchConversationDetail(convId);
      if (detail && detail.messages) {
        setMessages(detail.messages);
      } else {
        setMessages([]);
      }
    } catch (err) {
      console.error(`Failed to load messages for ${convId}:`, err);
      setMessages([]);
    }
  };

  const handleNewConversation = async () => {
    try {
      const newConv = await createConversation("New Conversation");
      setConversations(prev => [newConv, ...prev]);
      setActiveConversationId(newConv.id);
      sessionStorage.setItem('ruhi_active_conv_id', newConv.id);
      setMessages([]);
      setStreamingContent('');
      setErrorMessage(null);
      setLatestMemoryEvent(null);
    } catch (err) {
      console.error('Failed to create new conversation:', err);
    }
  };

  const handleRenameConversation = async (convId, newTitle) => {
    try {
      await renameConversation(convId, newTitle);
      setConversations(prev => prev.map(c => c.id === convId ? { ...c, title: newTitle } : c));
    } catch (err) {
      console.error('Failed to rename conversation:', err);
    }
  };

  const handleDeleteConversation = async (convId) => {
    try {
      await deleteConversation(convId);
      const remaining = conversations.filter(c => c.id !== convId);
      setConversations(remaining);

      if (activeConversationId === convId) {
        if (remaining.length > 0) {
          await handleSelectConversation(remaining[0].id);
        } else {
          await handleNewConversation();
        }
      }
    } catch (err) {
      console.error('Failed to delete conversation:', err);
    }
  };

  const suggestions = [
    { title: 'Test Persistent Memory', query: 'Remember that RUHI is my personal AI project.' },
    { title: 'Ask Recalled Context', query: 'What is RUHI?' },
    { title: 'Explain System Architecture', query: 'Explain the difference between short-term chat context and persistent PostgreSQL memory.' },
    { title: 'Plan Focus Workflow', query: 'I have 3 critical engineering tasks today. Help me structure an optimal focus workflow.' },
  ];

  const toggleVoiceInput = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  const handleSendMessage = async (textToSend) => {
    if (isListening) {
      stopListening();
    }

    const text = (textToSend || inputMessage).trim();
    if (!text || isThinking) return;

    setErrorMessage(null);
    setLatestMemoryEvent(null);
    const userMsg = { role: 'user', content: text, timestamp: new Date().toISOString() };
    setMessages((prev) => [...prev, userMsg]);
    setInputMessage('');
    setIsThinking(true);
    setStreamingContent('');

    let accumulated = '';

    await sendStreamingChatMessage({
      message: text,
      sessionId: activeConversationId,
      onStart: () => {
        setIsThinking(true);
      },
      onToken: (token) => {
        accumulated += token;
        setStreamingContent(accumulated);
      },
      onDone: () => {
        if (accumulated) {
          const assistantMsg = {
            role: 'assistant',
            content: accumulated,
            timestamp: new Date().toISOString(),
          };
          setMessages((prev) => [...prev, assistantMsg]);
        }
        setStreamingContent('');
        setIsThinking(false);
        refreshConversations();
        refreshMemoryCount();
      },
      onError: (err) => {
        console.warn('Streaming failed, falling back to standard request:', err);
        // Fallback to standard request
        sendChatMessage(text, activeConversationId)
          .then((res) => {
            const assistantMsg = {
              role: 'assistant',
              content: res.message,
              timestamp: res.timestamp || new Date().toISOString(),
            };
            setMessages((prev) => [...prev, assistantMsg]);
            if (res.memory_events && res.memory_events.length > 0) {
              setLatestMemoryEvent(res.memory_events[0]);
            }
          })
          .catch((fallbackErr) => {
            const displayError = fallbackErr.message || err.message || 'Failed to communicate with RUHI Core.';
            setErrorMessage(displayError);
            const errorMsg = {
              role: 'assistant',
              content: `RUHI encountered a communication issue: ${displayError}`,
              timestamp: new Date().toISOString(),
              isError: true,
            };
            setMessages((prev) => [...prev, errorMsg]);
          })
          .finally(() => {
            setStreamingContent('');
            setIsThinking(false);
            refreshConversations();
            refreshMemoryCount();
          });
      },
    });
  };

  const handleRetryLastMessage = () => {
    if (messages.length === 0) return;
    const lastUserMsg = [...messages].reverse().find(m => m.role === 'user');
    if (lastUserMsg) {
      if (messages[messages.length - 1]?.isError) {
        setMessages(prev => prev.slice(0, -1));
      }
      handleSendMessage(lastUserMsg.content);
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
      await clearSessionContext(activeConversationId);
      setMessages([]);
      setStreamingContent('');
      setErrorMessage(null);
      await refreshConversations();
    } catch (err) {
      console.error('Failed to reset session on server:', err);
      setMessages([]);
    }
  };

  const copyToClipboard = (text, idx) => {
    navigator.clipboard.writeText(text);
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
      if (match.index > lastIndex) {
        parts.push({
          type: 'text',
          content: content.slice(lastIndex, match.index),
        });
      }

      parts.push({
        type: 'code',
        language: match[1] || 'plaintext',
        code: match[2].trim(),
        id: snippetId++,
      });

      lastIndex = match.index + match[0].length;
    }

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

  const isOnline = backendHealth.online;

  return (
    <section className="ruhi-section" id="try-ruhi">
      <div className="ruhi-container">
        <div className="section-header">
          <div className="section-badge">
            <Sparkles size={13} />
            <span>RUHI STAGE 2 // PERSISTENT MEMORY & POSTGRESQL</span>
          </div>
          <h2 className="section-title">Try RUHI</h2>
          <p className="section-description">
            Experience RUHI's personal reasoning engine backed by persistent PostgreSQL memory. Tell RUHI facts or preferences to remember across sessions, and explore multi-turn context retention.
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
                <span className="console-title">RUHI Core</span>
                <span className="console-status-text">
                  <span className={`console-status-dot ${isOnline ? 'online' : 'offline'}`} />
                  {isOnline ? 'RUHI Online' : 'RUHI Offline (Backend disconnected)'}
                </span>
              </div>
            </div>

            <div className="console-actions-group">
              {/* History Sidebar Toggle */}
              <button
                onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                className={`btn-console-tool ${isSidebarOpen ? 'active' : ''}`}
                title="Toggle Conversation History Sidebar"
              >
                <History size={13} />
                <span>History ({conversations.length})</span>
              </button>

              {/* Memory Modal Trigger */}
              <button
                onClick={() => setIsMemoryModalOpen(true)}
                className="btn-console-tool memory-btn"
                title="View & Manage Persistent Long-Term Memories"
              >
                <Brain size={13} />
                <span>Memory ({memoryCount})</span>
              </button>

              <div className="context-counter-pill">
                <Cpu size={12} color="var(--cyan-primary)" />
                <span>Turns: {messages.length}</span>
              </div>

              {messages.length > 0 && (
                <button 
                  onClick={handleClearContext}
                  className="btn-console-clear"
                  aria-label="Clear active conversation session context"
                  title="Clear messages for this conversation"
                >
                  <Trash2 size={13} />
                  <span>Reset</span>
                </button>
              )}
            </div>
          </div>

          {/* Body Layout: Sidebar + Main Chat Viewport */}
          <div className="chat-body-layout">
            {/* Conversation History Sidebar */}
            <ChatSidebar
              isOpen={isSidebarOpen}
              onToggle={() => setIsSidebarOpen(!isSidebarOpen)}
              conversations={conversations}
              activeConversationId={activeConversationId}
              onSelectConversation={handleSelectConversation}
              onNewConversation={handleNewConversation}
              onRenameConversation={handleRenameConversation}
              onDeleteConversation={handleDeleteConversation}
            />

            {/* Main Chat Viewport */}
            <div className="chat-viewport">
              {/* Conversation Area */}
              <div ref={messagesContainerRef} className="chat-messages-container">
                {messages.length === 0 && !streamingContent ? (
                  <div className="chat-welcome-state">
                    <img src="/ruhi-icon.svg" alt="RUHI Glyph" className="welcome-glyph" />
                    <h3 className="welcome-heading">How may RUHI assist you today?</h3>
                    <p className="welcome-desc">
                      Say <em>"Remember that..."</em> to store persistent context, ask questions, or pick a scenario below to explore multi-turn reasoning and persistent memory.
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
                        {msg.role === 'assistant' && !msg.isError && (
                          <div className="message-toolbar">
                            <button
                              onClick={() => copyToClipboard(msg.content, `msg_${idx}`)}
                              className="btn-message-tool"
                              aria-label="Copy response"
                            >
                              {copiedIndex === `msg_${idx}` ? (
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
                        )}
                      </div>
                    </div>
                  ))
                )}

                {/* Live Streaming Token Box */}
                {streamingContent && (
                  <div className="message-row ruhi">
                    <div className="message-avatar">
                      <Sparkles size={16} />
                    </div>
                    <div className="message-content-box">
                      {renderMessageContent(streamingContent)}
                      <span className="streaming-cursor" />
                    </div>
                  </div>
                )}

                {/* Calm Thinking State */}
                {isThinking && !streamingContent && (
                  <div className="ruhi-thinking-indicator">
                    <div className="thinking-waves">
                      <div className="wave-bar" />
                      <div className="wave-bar" />
                      <div className="wave-bar" />
                    </div>
                    <span>RUHI is reasoning through your request...</span>
                  </div>
                )}

                {/* Error & Retry Bar */}
                {errorMessage && (
                  <div className="chat-error-banner">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <AlertCircle size={15} color="#f87171" />
                      <span>{errorMessage}</span>
                    </div>
                    <button 
                      onClick={handleRetryLastMessage}
                      className="btn-retry"
                    >
                      <RotateCcw size={13} />
                      <span>Retry</span>
                    </button>
                  </div>
                )}
              </div>

              {/* Composer */}
              <div className="chat-composer-area">
                {/* Voice Status Indicator Banner */}
                <VoiceStatusBanner 
                  voiceState={voiceState}
                  errorMessage={voiceError}
                  interimTranscript={interimTranscript}
                  onDismiss={resetVoiceState}
                  onRetry={startListening}
                />

                <form className="composer-form" onSubmit={(e) => { e.preventDefault(); handleSendMessage(); }}>
                  <input
                    ref={inputRef}
                    type="text"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder={isListening ? 'Listening to your speech...' : 'Talk to RUHI (type or dictate with mic)...'}
                    className={`composer-input ${isListening ? 'active-listening' : ''}`}
                    disabled={isThinking}
                    aria-label="Input prompt for RUHI"
                  />

                  <button
                    type="button"
                    onClick={toggleVoiceInput}
                    className={`btn-composer-voice ${isListening ? 'listening' : ''}`}
                    title={isListening ? 'Stop listening' : 'Start voice input (speech-to-text)'}
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
                  Press Enter to send • Shift + Enter for newline • 🎙️ Voice-to-text active • 🧠 Stored in PostgreSQL (<code>ruhi-web</code>)
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Memory Management Modal */}
      <MemoryModal
        isOpen={isMemoryModalOpen}
        onClose={() => {
          setIsMemoryModalOpen(false);
          refreshMemoryCount();
        }}
      />
    </section>
  );
}
