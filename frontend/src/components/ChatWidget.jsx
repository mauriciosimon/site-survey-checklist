import { useState, useRef, useEffect } from 'react';
import { MessageCircle, X, Send, Bot, User, Loader2 } from 'lucide-react';
import { useWorkspace } from '../WorkspaceContext';
import { chatApi } from '../api';

export default function ChatWidget() {
  const { currentWorkspace } = useWorkspace();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Focus input when chat opens
  useEffect(() => {
    if (isOpen) {
      inputRef.current?.focus();
    }
  }, [isOpen]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading || !currentWorkspace) return;

    const userMessage = inputValue.trim();
    setInputValue('');

    // Add user message to chat
    const newMessages = [...messages, { role: 'user', content: userMessage }];
    setMessages(newMessages);

    setIsLoading(true);
    try {
      // Build conversation history (last 10 messages for context)
      const conversationHistory = newMessages.slice(-10).map(msg => ({
        role: msg.role,
        content: msg.content,
      }));

      const response = await chatApi.sendMessage({
        message: userMessage,
        workspace_id: currentWorkspace.id,
        conversation_history: conversationHistory.slice(0, -1), // Exclude the message we just added
      });

      // Add AI response
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.data.response,
      }]);
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        isError: true,
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Don't render if no workspace is selected
  if (!currentWorkspace) return null;

  return (
    <>
      {/* Chat Widget Bubble */}
      {!isOpen && (
        <button
          className="chat-widget-bubble"
          onClick={() => setIsOpen(true)}
          title="Chat with West Park AI"
        >
          <MessageCircle size={24} />
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className="chat-widget-window">
          {/* Header */}
          <div className="chat-widget-header">
            <div className="chat-widget-header-info">
              <Bot size={20} />
              <div>
                <span className="chat-widget-title">West Park AI</span>
                <span className="chat-widget-workspace">{currentWorkspace.name}</span>
              </div>
            </div>
            <button
              className="chat-widget-close"
              onClick={() => setIsOpen(false)}
            >
              <X size={20} />
            </button>
          </div>

          {/* Messages Area */}
          <div className="chat-widget-messages">
            {messages.length === 0 && (
              <div className="chat-widget-welcome">
                <Bot size={32} />
                <p>Hi! I'm West Park AI, your CRM assistant.</p>
                <p className="chat-widget-welcome-hint">
                  Ask me about priorities, summaries, or anything about your {currentWorkspace.name} data.
                </p>
              </div>
            )}
            {messages.map((message, index) => (
              <div
                key={index}
                className={`chat-message ${message.role} ${message.isError ? 'error' : ''}`}
              >
                <div className="chat-message-icon">
                  {message.role === 'user' ? <User size={16} /> : <Bot size={16} />}
                </div>
                <div className="chat-message-content">
                  {message.content}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="chat-message assistant loading">
                <div className="chat-message-icon">
                  <Bot size={16} />
                </div>
                <div className="chat-message-content">
                  <Loader2 size={16} className="spin" />
                  <span>Thinking...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="chat-widget-input-area">
            <textarea
              ref={inputRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about your data..."
              rows={1}
              disabled={isLoading}
            />
            <button
              className="chat-widget-send"
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isLoading}
            >
              <Send size={18} />
            </button>
          </div>
        </div>
      )}
    </>
  );
}
