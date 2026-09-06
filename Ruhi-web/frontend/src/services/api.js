const envApiUrl = import.meta.env.VITE_API_URL;
const API_BASE = envApiUrl
  ? (envApiUrl.endsWith('/api') ? envApiUrl : `${envApiUrl.replace(/\/$/, '')}/api`)
  : (typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    ? 'http://127.0.0.1:8000/api'
    : '/api');

// -----------------------------------------------------------------------------
// Chat & Streaming Methods
// -----------------------------------------------------------------------------

/**
 * Sends a standard synchronous chat message to RUHI AI Core with persistent context.
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
        conversation_id: sessionId,
        context,
        stream: false,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || errorData.error || errorData.message || `HTTP error ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error sending message to RUHI Core:', error);
    throw error;
  }
}

/**
 * Sends a message and receives real-time SSE streamed tokens with persistent context.
 */
export async function sendStreamingChatMessage({
  message,
  sessionId,
  context = {},
  onToken,
  onStart,
  onDone,
  onError,
}) {
  try {
    const response = await fetch(`${API_BASE}/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        session_id: sessionId,
        conversation_id: sessionId,
        context,
        stream: true,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const errMsg = errorData.detail || errorData.error || errorData.message || `HTTP error ${response.status}`;
      if (onError) onError(new Error(errMsg));
      return;
    }

    if (!response.body) {
      throw new Error('ReadableStream not supported by browser or empty response body');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        const trimmed = line.trim();
        if (trimmed.startsWith('data:')) {
          const jsonStr = trimmed.replace(/^data:\s*/, '');
          if (!jsonStr) continue;

          try {
            const data = JSON.parse(jsonStr);
            if (data.type === 'start') {
              if (onStart) onStart(data);
            } else if (data.type === 'token') {
              if (onToken) onToken(data.token);
            } else if (data.type === 'done') {
              if (onDone) onDone(data);
            } else if (data.type === 'error') {
              if (onError) onError(new Error(data.error || 'Streaming error'));
            }
          } catch (parseErr) {
            console.warn('Error parsing SSE event:', parseErr, jsonStr);
          }
        }
      }
    }

    if (onDone) onDone({ session_id: sessionId, conversation_id: sessionId });
  } catch (error) {
    console.error('Error in streaming chat:', error);
    if (onError) onError(error);
  }
}

/**
 * Resets active session conversation context in RUHI Core
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

// -----------------------------------------------------------------------------
// Persistent Conversations API (Stage 2)
// -----------------------------------------------------------------------------

export async function fetchConversations(limit = 50, offset = 0) {
  try {
    const response = await fetch(`${API_BASE}/conversations?limit=${limit}&offset=${offset}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error('Error fetching conversations:', error);
    return [];
  }
}

export async function createConversation(title = "New Conversation") {
  try {
    const response = await fetch(`${API_BASE}/conversations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title }),
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error('Error creating conversation:', error);
    throw error;
  }
}

export async function fetchConversationDetail(conversationId) {
  try {
    const response = await fetch(`${API_BASE}/conversations/${encodeURIComponent(conversationId)}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error(`Error loading conversation ${conversationId}:`, error);
    throw error;
  }
}

export async function renameConversation(conversationId, title) {
  try {
    const response = await fetch(`${API_BASE}/conversations/${encodeURIComponent(conversationId)}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title }),
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error(`Error renaming conversation ${conversationId}:`, error);
    throw error;
  }
}

export async function deleteConversation(conversationId) {
  try {
    const response = await fetch(`${API_BASE}/conversations/${encodeURIComponent(conversationId)}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error(`Error deleting conversation ${conversationId}:`, error);
    throw error;
  }
}

// -----------------------------------------------------------------------------
// Persistent Long-Term Memory API (Stage 2)
// -----------------------------------------------------------------------------

export async function fetchMemories({ type = null, search = null, active = true, limit = 50, offset = 0 } = {}) {
  try {
    const params = new URLSearchParams();
    if (type && type !== 'all') params.append('type', type);
    if (search && search.trim()) params.append('search', search.trim());
    params.append('active', String(active));
    params.append('limit', String(limit));
    params.append('offset', String(offset));

    const response = await fetch(`${API_BASE}/memories?${params.toString()}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error('Error fetching memories:', error);
    return { memories: [], total: 0 };
  }
}

export async function createMemory({ content, memory_type = 'general', importance = 5, source = 'explicit' }) {
  try {
    const response = await fetch(`${API_BASE}/memories`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content, memory_type, importance, source }),
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error('Error creating memory:', error);
    throw error;
  }
}

export async function updateMemory(memoryId, { content, memory_type, importance, is_active }) {
  try {
    const response = await fetch(`${API_BASE}/memories/${encodeURIComponent(memoryId)}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content, memory_type, importance, is_active }),
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error(`Error updating memory ${memoryId}:`, error);
    throw error;
  }
}

export async function deleteMemory(memoryId, hard = false) {
  try {
    const response = await fetch(`${API_BASE}/memories/${encodeURIComponent(memoryId)}?hard=${hard}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error(`Error deleting memory ${memoryId}:`, error);
    throw error;
  }
}

// -----------------------------------------------------------------------------
// Health & Capabilities API
// -----------------------------------------------------------------------------

export async function checkBackendHealth() {
  try {
    const response = await fetch(`${API_BASE}/health`);
    if (!response.ok) throw new Error('Backend health check failed');
    return await response.json();
  } catch (error) {
    return {
      status: 'offline',
      service: 'RUHI AI Core',
      database_connected: false,
      database_name: 'ruhi-web',
      configured_api_key: false,
      active_sessions: 0,
      persistent_memories_count: 0,
      streaming_supported: false,
    };
  }
}

export async function fetchCapabilities() {
  try {
    const response = await fetch(`${API_BASE}/tools`);
    if (!response.ok) throw new Error('Failed to fetch tools');
    return await response.json();
  } catch (error) {
    console.error('Error loading capabilities:', error);
    return null;
  }
}

export async function executeTool(toolName, args = {}) {
  try {
    const response = await fetch(`${API_BASE}/tools/execute`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        tool_name: toolName,
        arguments: args,
      }),
    });

    if (!response.ok) {
      throw new Error(`Tool execution failed: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`Error executing tool ${toolName}:`, error);
    throw error;
  }
}
