import { useState, useEffect, useRef, useCallback } from 'react';

/**
 * useSpeechRecognition
 * 
 * Custom hook providing robust Web Speech API lifecycle management for RUHI Voice Input.
 * 
 * States:
 * - 'idle': Microphone ready for interaction
 * - 'listening': Actively capturing audio stream and transcribing speech
 * - 'processing': Finalizing transcript
 * - 'permission_denied': User denied microphone access
 * - 'unsupported': Browser lacks Web Speech API support
 * - 'error': Hardware, audio capture, or network failure
 */
export function useSpeechRecognition({ onTranscript, onFinalTranscript } = {}) {
  const [voiceState, setVoiceState] = useState('idle');
  const [errorMessage, setErrorMessage] = useState(null);
  const [interimTranscript, setInterimTranscript] = useState('');
  
  const recognitionRef = useRef(null);
  const isMountedRef = useRef(true);
  const onTranscriptRef = useRef(onTranscript);
  const onFinalTranscriptRef = useRef(onFinalTranscript);

  // Keep callback refs fresh without causing effect re-runs
  useEffect(() => {
    onTranscriptRef.current = onTranscript;
    onFinalTranscriptRef.current = onFinalTranscript;
  }, [onTranscript, onFinalTranscript]);

  // Initial check for SpeechRecognition support
  useEffect(() => {
    isMountedRef.current = true;
    const SpeechRecognitionClass = typeof window !== 'undefined'
      ? (window.SpeechRecognition || window.webkitSpeechRecognition)
      : null;

    if (!SpeechRecognitionClass) {
      setVoiceState('unsupported');
    }

    return () => {
      isMountedRef.current = false;
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort();
        } catch (_) {}
        recognitionRef.current = null;
      }
    };
  }, []);

  const stopListening = useCallback(() => {
    if (!recognitionRef.current) {
      setVoiceState('idle');
      return;
    }
    try {
      setVoiceState('processing');
      recognitionRef.current.stop();
    } catch (_) {
      setVoiceState('idle');
    }
  }, []);

  const startListening = useCallback(() => {
    const SpeechRecognitionClass = typeof window !== 'undefined'
      ? (window.SpeechRecognition || window.webkitSpeechRecognition)
      : null;

    if (!SpeechRecognitionClass) {
      setVoiceState('unsupported');
      setErrorMessage('Voice input is not supported in this browser. Please use Chrome, Edge, or Safari.');
      return;
    }

    // Abort existing instance before starting a new one
    if (recognitionRef.current) {
      try {
        recognitionRef.current.abort();
      } catch (_) {}
      recognitionRef.current = null;
    }

    try {
      const recognition = new SpeechRecognitionClass();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = (typeof navigator !== 'undefined' && navigator.language) ? navigator.language : 'en-US';
      recognition.maxAlternatives = 1;

      recognition.onstart = () => {
        if (!isMountedRef.current) return;
        setVoiceState('listening');
        setErrorMessage(null);
        setInterimTranscript('');
      };

      recognition.onresult = (event) => {
        if (!isMountedRef.current) return;
        let interim = '';
        let final = '';

        for (let i = event.resultIndex; i < event.results.length; ++i) {
          const chunk = event.results[i][0]?.transcript || '';
          if (event.results[i].isFinal) {
            final += chunk;
          } else {
            interim += chunk;
          }
        }

        if (interim) {
          setInterimTranscript(interim);
          onTranscriptRef.current?.(interim);
        }

        if (final) {
          setInterimTranscript('');
          if (onFinalTranscriptRef.current) {
            onFinalTranscriptRef.current(final);
          } else if (onTranscriptRef.current) {
            onTranscriptRef.current(final);
          }
        }
      };

      recognition.onerror = (event) => {
        if (!isMountedRef.current) return;
        console.warn('SpeechRecognition error:', event.error);
        
        if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
          setVoiceState('permission_denied');
          setErrorMessage('Microphone access was denied. Please allow microphone access in your browser address bar settings.');
        } else if (event.error === 'no-speech') {
          // In continuous mode, silence does not require erroring out immediately
        } else if (event.error === 'audio-capture') {
          setVoiceState('error');
          setErrorMessage('No microphone device detected. Please verify your audio hardware is connected.');
        } else if (event.error === 'network') {
          setVoiceState('error');
          setErrorMessage('Speech recognition network error. Please verify your internet connection.');
        } else if (event.error !== 'aborted') {
          setVoiceState('error');
          setErrorMessage(`Voice recognition error: ${event.error}`);
        }
      };

      recognition.onend = () => {
        if (!isMountedRef.current) return;
        setInterimTranscript('');
        recognitionRef.current = null;
        setVoiceState((prev) => {
          if (prev === 'permission_denied' || prev === 'unsupported' || prev === 'error') {
            return prev;
          }
          return 'idle';
        });
      };

      recognitionRef.current = recognition;
      setVoiceState('listening');
      setErrorMessage(null);
      recognition.start();
    } catch (err) {
      console.error('Failed to start SpeechRecognition:', err);
      setVoiceState('error');
      setErrorMessage('Could not initialize speech recognition. Please check your browser microphone permissions.');
    }
  }, []);

  const resetVoiceState = useCallback(() => {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.abort();
      } catch (_) {}
      recognitionRef.current = null;
    }
    setVoiceState('idle');
    setErrorMessage(null);
    setInterimTranscript('');
  }, []);

  return {
    voiceState, // 'idle' | 'listening' | 'processing' | 'permission_denied' | 'unsupported' | 'error'
    isListening: voiceState === 'listening',
    isProcessing: voiceState === 'processing',
    isSupported: voiceState !== 'unsupported',
    errorMessage,
    interimTranscript,
    startListening,
    stopListening,
    resetVoiceState,
  };
}
