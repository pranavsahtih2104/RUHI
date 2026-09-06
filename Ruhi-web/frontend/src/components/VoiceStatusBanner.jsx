import React from 'react';
import { Mic, AlertCircle, ShieldAlert, X, RefreshCw, Volume2 } from 'lucide-react';

export default function VoiceStatusBanner({ voiceState, errorMessage, interimTranscript, onDismiss, onRetry }) {
  if (voiceState === 'idle') return null;

  if (voiceState === 'listening') {
    return (
      <div className="voice-status-banner listening">
        <div className="voice-pulse-circle" />
        <div className="voice-banner-text">
          <strong>RUHI is listening...</strong>
          <span>
            {interimTranscript ? (
              <em>Hearing: "{interimTranscript}"</em>
            ) : (
              'Speak clearly into your microphone. Words will appear in the input box.'
            )}
          </span>
        </div>
      </div>
    );
  }

  if (voiceState === 'processing') {
    return (
      <div className="voice-status-banner processing">
        <RefreshCw size={14} className="spin-icon" />
        <div className="voice-banner-text">
          <span>Processing voice transcript...</span>
        </div>
      </div>
    );
  }

  if (voiceState === 'permission_denied') {
    return (
      <div className="voice-status-banner error">
        <ShieldAlert size={16} color="#f87171" />
        <div className="voice-banner-text">
          <strong>Microphone permission required</strong>
          <span>{errorMessage || 'Please allow microphone access in your browser settings to speak to RUHI.'}</span>
        </div>
        {onDismiss && (
          <button onClick={onDismiss} className="btn-voice-banner-close" aria-label="Dismiss alert">
            <X size={14} />
          </button>
        )}
      </div>
    );
  }

  if (voiceState === 'unsupported') {
    return (
      <div className="voice-status-banner warning">
        <AlertCircle size={16} color="#fbbf24" />
        <div className="voice-banner-text">
          <strong>Voice input unsupported</strong>
          <span>Speech recognition is not supported in this browser. Please use Chrome, Edge, or Safari, or type your message.</span>
        </div>
        {onDismiss && (
          <button onClick={onDismiss} className="btn-voice-banner-close" aria-label="Dismiss alert">
            <X size={14} />
          </button>
        )}
      </div>
    );
  }

  if (voiceState === 'error') {
    return (
      <div className="voice-status-banner error">
        <AlertCircle size={16} color="#f87171" />
        <div className="voice-banner-text">
          <strong>Voice Input Error</strong>
          <span>{errorMessage || 'An error occurred with voice recognition.'}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {onRetry && (
            <button onClick={onRetry} className="btn-voice-banner-action">
              Retry
            </button>
          )}
          {onDismiss && (
            <button onClick={onDismiss} className="btn-voice-banner-close" aria-label="Dismiss alert">
              <X size={14} />
            </button>
          )}
        </div>
      </div>
    );
  }

  return null;
}
