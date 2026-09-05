const envApiUrl = import.meta.env.VITE_API_URL;
const API_BASE = envApiUrl
  ? (envApiUrl.endsWith('/api') ? envApiUrl : `${envApiUrl.replace(/\/$/, '')}/api`)
  : (typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    ? 'http://127.0.0.1:8000/api'
    : '/api');

/**
 * Sends a message to the RUHI AI backend
 * @param {string} message 
 * @param {string} sessionId 
 * @param {object} context 
 */
export async function sendChatMessage(message, sessionId, context = {}) {
  try {
    const response = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        session_id: sessionId,
        context,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || errorData.message || `HTTP error ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error sending message to RUHI backend:', error);
    throw error;
  }
}

/**
 * Resets active session conversation context
 * @param {string} sessionId 
 */
export async function clearSessionContext(sessionId) {
  try {
    const response = await fetch(`${API_BASE}/chat/clear`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        session_id: sessionId,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to clear session: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error clearing session:', error);
    throw error;
  }
}

/**
 * Fetches backend health and model provider status
 */
export async function checkBackendHealth() {
  try {
    const response = await fetch(`${API_BASE}/health`);
    if (!response.ok) throw new Error('Backend health check failed');
    return await response.json();
  } catch (error) {
    console.warn('Backend unavailable, running in local fallback mode:', error);
    return {
      status: 'offline_or_fallback',
      llm_provider: 'Local Simulator',
      model: 'ruhi-core-fallback',
      configured_api_key: false,
    };
  }
}

/**
 * Fetches structured capabilities from the backend
 */
export async function fetchCapabilities() {
  try {
    const response = await fetch(`${API_BASE}/capabilities`);
    if (!response.ok) throw new Error('Failed to fetch capabilities');
    return await response.json();
  } catch (error) {
    console.error('Error loading capabilities:', error);
    return null;
  }
}
