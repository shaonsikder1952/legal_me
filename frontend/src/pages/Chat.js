import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import { Send, ArrowLeft, Loader2 } from 'lucide-react';
import ChatHistory from '../components/ChatHistory';
import TypingAnimation from '../components/TypingAnimation';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Chat = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(() => `session_${Date.now()}`);
  const [typingMessageIndex, setTypingMessageIndex] = useState(null);
  const messagesEndRef = useRef(null);

  const loadSessionMessages = async (sid) => {
    try {
      const response = await axios.get(`${API}/chat/${sid}/messages`);
      const loadedMessages = response.data.map(msg => ([
        { role: 'user', content: msg.user_message },
        { role: 'assistant', content: msg.ai_response }
      ])).flat();
      setMessages(loadedMessages);
      setSessionId(sid);
    } catch (error) {
      console.error('Error loading session:', error);
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    setSessionId(`session_${Date.now()}`);
  };

  useEffect(() => {
    if (location.state?.initialTopic) {
      const topicMessage = `Tell me about ${location.state.initialTopic} in Germany.`;
      setMessages([{ role: 'user', content: topicMessage }]);
      sendMessage(topicMessage);
    }
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async (messageText) => {
    const textToSend = messageText || input;
    if (!textToSend.trim()) return;

    if (!messageText) {
      setMessages(prev => [...prev, { role: 'user', content: textToSend }]);
    }
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post(`${API}/chat`, {
        session_id: sessionId,
        message: textToSend
      });

      const newMessage = { role: 'assistant', content: response.data.response, isTyping: true };
      setMessages(prev => [...prev, newMessage]);
      setTypingMessageIndex(messages.length + 1);
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage();
  };

  return (
    <div className="min-h-screen bg-stone-50 flex items-center justify-center p-4">
      <ChatHistory 
        onSelectSession={loadSessionMessages} 
        currentSessionId={sessionId}
        onNewChat={handleNewChat}
      />
      <div className="max-w-3xl w-full h-[calc(100vh-4rem)] flex flex-col bg-white shadow-2xl shadow-stone-200/50 rounded-t-3xl border-x border-t border-stone-100">
        {/* Header */}
        <div className="p-6 border-b border-stone-100 flex items-center justify-between bg-white rounded-t-3xl">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/')}
              className="w-10 h-10 rounded-full hover:bg-stone-100 flex items-center justify-center"
              data-testid="back-button"
            >
              <ArrowLeft className="w-5 h-5 text-stone-600" />
            </button>
            <div>
              <h1 className="font-serif text-2xl text-stone-900">LegalMe Chat</h1>
              <p className="text-sm text-stone-500">Ask any legal question</p>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6" data-testid="chat-messages">
          {messages.length === 0 && (
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-3xl">⚖️</span>
              </div>
              <h2 className="font-serif text-xl text-stone-900 mb-2">How can I help you today?</h2>
              <p className="text-stone-500">Ask about rental agreements, employment contracts, or any legal topic.</p>
            </div>
          )}

          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {message.role === 'user' ? (
                <div 
                  className="bg-stone-100 text-stone-900 rounded-2xl rounded-tr-sm px-6 py-4 max-w-[85%]"
                  data-testid={`user-message-${index}`}
                >
                  {message.content}
                </div>
              ) : (
                <div 
                  className="bg-white border border-stone-100 text-stone-800 rounded-2xl rounded-tl-sm px-6 py-6 max-w-[95%] shadow-sm prose prose-stone"
                  data-testid={`ai-message-${index}`}
                >
                  {message.isTyping && typingMessageIndex === index ? (
                    <TypingAnimation
                      content={message.content}
                      speed={15}
                      onComplete={() => {
                        setTypingMessageIndex(null);
                        setMessages(prev => prev.map((msg, idx) => 
                          idx === index ? { ...msg, isTyping: false } : msg
                        ));
                      }}
                    />
                  ) : (
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      rehypePlugins={[rehypeRaw]}
                      components={{
                        a: ({node, ...props}) => (
                          <a {...props} target="_blank" rel="noopener noreferrer" className="text-orange-700 hover:underline font-medium" />
                        )
                      }}
                    >
                      {message.content}
                    </ReactMarkdown>
                  )}
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div className="bg-white border border-stone-100 rounded-2xl rounded-tl-sm px-6 py-4 shadow-sm">
                <Loader2 className="w-5 h-5 text-orange-600 animate-spin" />
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="p-6 border-t border-stone-100 bg-white">
          <form onSubmit={handleSubmit} className="flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a legal question..."
              className="flex-1 bg-stone-50 border-stone-200 focus:border-orange-500 focus:ring-orange-500/20 rounded-xl h-12 px-4 focus:outline-none focus:ring-2"
              disabled={loading}
              data-testid="chat-input"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="bg-orange-700 text-white hover:bg-orange-800 h-12 w-12 rounded-full font-medium shadow-lg shadow-orange-900/20 hover:shadow-orange-900/30 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
              data-testid="send-button"
            >
              <Send className="w-5 h-5" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Chat;