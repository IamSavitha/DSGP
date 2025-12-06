import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, Loader2, AlertCircle, MessageCircle, Sparkles } from 'lucide-react';
import { sendChatMessage, getChatSession, ChatMessage, ChatResponse } from '../api/chat';
import { useAuth } from '../context/AuthContext';

const ChatPage: React.FC = () => {
  const { user } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Load existing session if sessionId is in localStorage
  useEffect(() => {
    const savedSessionId = localStorage.getItem('chat_session_id');
    if (savedSessionId) {
      setSessionId(savedSessionId);
      loadChatSession(savedSessionId);
    } else {
      // Start with welcome message
      setMessages([{
        role: 'assistant',
        content: "Hello! I'm your AI travel concierge. I can help you find the perfect trip - flights, hotels, cars, or complete bundles. What are you looking for?",
        timestamp: new Date().toISOString()
      }]);
    }
  }, []);

  const loadChatSession = async (sessionId: string) => {
    try {
      const session = await getChatSession(sessionId);
      setMessages(session.messages || []);
    } catch (err: any) {
      console.error('Failed to load chat session:', err);
      // Start fresh if session load fails
      setMessages([{
        role: 'assistant',
        content: "Hello! I'm your AI travel concierge. I can help you find the perfect trip - flights, hotels, cars, or complete bundles. What are you looking for?",
        timestamp: new Date().toISOString()
      }]);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!inputMessage.trim() || loading) {
      return;
    }

    const userMessage: ChatMessage = {
      role: 'user',
      content: inputMessage.trim(),
      timestamp: new Date().toISOString()
    };

    // Add user message immediately
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);
    setError(null);

    try {
      const response: ChatResponse = await sendChatMessage({
        message: userMessage.content,
        user_id: user?.user_id || undefined,
        session_id: sessionId || undefined
      });

      // Save session ID if this is a new session
      if (response.session_id && !sessionId) {
        setSessionId(response.session_id);
        localStorage.setItem('chat_session_id', response.session_id);
      }

      // Add assistant response
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.message,
        timestamp: new Date().toISOString(),
        recommendations: response.bundles,
        clarification_needed: response.clarification_needed
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err: any) {
      setError(err.message || 'Failed to send message. Please try again.');
      console.error('Error sending message:', err);
      
      // Remove user message on error
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setLoading(false);
    }
  };

  const handleNewChat = () => {
    setMessages([{
      role: 'assistant',
      content: "Hello! I'm your AI travel concierge. I can help you find the perfect trip - flights, hotels, cars, or complete bundles. What are you looking for?",
      timestamp: new Date().toISOString()
    }]);
    setSessionId(null);
    localStorage.removeItem('chat_session_id');
    setError(null);
  };

  const formatTime = (timestamp?: string) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100/30 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8 text-center">
          <div className="inline-flex items-center space-x-3 mb-4">
            <div className="p-3 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl shadow-lg">
              <Sparkles className="text-white" size={32} />
            </div>
            <div>
              <h1 className="text-4xl font-bold text-slate-900">Travel Concierge</h1>
              <p className="text-slate-600">AI-powered travel assistant</p>
            </div>
          </div>
          <button
            onClick={handleNewChat}
            className="text-sm text-blue-600 hover:text-blue-800 font-medium"
          >
            Start New Chat
          </button>
        </div>

        {/* Chat Container */}
        <div className="bg-white rounded-2xl border-2 border-slate-200 shadow-xl overflow-hidden flex flex-col" style={{ height: '70vh' }}>
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex items-start space-x-3 ${
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                {message.role === 'assistant' && (
                  <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center shadow-md">
                    <Bot className="text-white" size={20} />
                  </div>
                )}
                
                <div
                  className={`max-w-[75%] rounded-2xl px-4 py-3 shadow-md ${
                    message.role === 'user'
                      ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white'
                      : 'bg-slate-100 text-slate-900'
                  }`}
                >
                  <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
                  {message.timestamp && (
                    <p
                      className={`text-xs mt-1 ${
                        message.role === 'user' ? 'text-blue-100' : 'text-slate-500'
                      }`}
                    >
                      {formatTime(message.timestamp)}
                    </p>
                  )}
                  
                  {message.recommendations && message.recommendations.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-slate-300">
                      <p className="text-xs font-semibold mb-2">Recommended Bundles:</p>
                      {message.recommendations.slice(0, 2).map((bundle: any, idx: number) => (
                        <div key={idx} className="text-xs bg-white/50 rounded-lg p-2 mb-2">
                          <p className="font-semibold">{bundle.bundle_id}</p>
                          <p>Total: ${bundle.total_price?.toFixed(2)}</p>
                          <p>Fit Score: {bundle.fit_score}/100</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
                
                {message.role === 'user' && (
                  <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-slate-400 to-slate-500 rounded-full flex items-center justify-center shadow-md">
                    <User className="text-white" size={20} />
                  </div>
                )}
              </div>
            ))}
            
            {loading && (
              <div className="flex items-start space-x-3 justify-start">
                <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center shadow-md">
                  <Bot className="text-white" size={20} />
                </div>
                <div className="bg-slate-100 rounded-2xl px-4 py-3 shadow-md">
                  <Loader2 className="animate-spin text-blue-600" size={20} />
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Error Message */}
          {error && (
            <div className="px-6 pb-2">
              <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg flex items-center space-x-3">
                <AlertCircle size={20} />
                <span className="text-sm">{error}</span>
              </div>
            </div>
          )}

          {/* Input Area */}
          <div className="border-t border-slate-200 p-4">
            <form onSubmit={handleSendMessage} className="flex items-center space-x-3">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Ask me anything about travel..."
                className="flex-1 px-4 py-3 rounded-xl border-2 border-slate-300 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200 text-slate-900 placeholder:text-slate-400"
                disabled={loading}
              />
              <button
                type="submit"
                disabled={!inputMessage.trim() || loading}
                className="p-3 bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-xl hover:from-blue-600 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md hover:shadow-lg flex items-center justify-center"
              >
                {loading ? (
                  <Loader2 className="animate-spin" size={20} />
                ) : (
                  <Send size={20} />
                )}
              </button>
            </form>
            <p className="text-xs text-slate-500 mt-2 text-center">
              Try asking: "I want to find a trip to Miami" or "What are the best deals?"
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;

