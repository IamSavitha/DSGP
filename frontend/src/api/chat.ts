const AI_API_BASE_URL = '/api/ai';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
  recommendations?: any[];
  clarification_needed?: boolean;
}

export interface ChatRequest {
  message: string;
  user_id?: string;
  session_id?: string;
}

export interface ChatResponse {
  message: string;
  bundles?: any[];
  clarification_needed?: boolean;
  context?: Record<string, any>;
  session_id: string;
}

export interface ChatSession {
  session_id: string;
  user_id?: string;
  messages: ChatMessage[];
  context?: Record<string, any>;
  started_at: string;
  last_activity: string;
  ended_at?: string;
}

/**
 * Send a chat message to the concierge agent
 */
export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  const response = await fetch(`${AI_API_BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to send chat message');
  }

  return response.json();
}

/**
 * Get chat session history
 */
export async function getChatSession(sessionId: string): Promise<ChatSession> {
  const response = await fetch(`${AI_API_BASE_URL}/chat/sessions/${sessionId}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get chat session');
  }

  return response.json();
}

