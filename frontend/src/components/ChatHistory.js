import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { MessageSquare, X, Clock, Plus, Edit2, Trash2, Menu } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ChatHistory = ({ onSelectSession, currentSessionId, onNewChat }) => {
  const [sessions, setSessions] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [editName, setEditName] = useState('');

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/chat/history`);
      setSessions(response.data);
    } catch (error) {
      console.error('Error loading chat history:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    const now = new Date();
    const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    return date.toLocaleDateString();
  };

  return (
    <>
      {/* Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed left-4 top-4 z-50 w-12 h-12 bg-orange-700 text-white rounded-full shadow-lg hover:bg-orange-800 flex items-center justify-center"
        data-testid="chat-history-toggle"
      >
        {isOpen ? <X className="w-6 h-6" /> : <Clock className="w-6 h-6" />}
      </button>

      {/* Sidebar */}
      {isOpen && (
        <div className="fixed left-0 top-0 bottom-0 w-80 bg-white border-r border-stone-200 shadow-xl z-40 overflow-y-auto">
          <div className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <MessageSquare className="w-6 h-6 text-orange-700" />
              <h2 className="font-serif text-2xl text-stone-900">Chat History</h2>
            </div>

            {loading ? (
              <div className="text-center py-8 text-stone-500">Loading...</div>
            ) : sessions.length === 0 ? (
              <div className="text-center py-8 text-stone-500">No chat history yet</div>
            ) : (
              <div className="space-y-2">
                {sessions.map((session) => (
                  <button
                    key={session.session_id}
                    onClick={() => {
                      onSelectSession(session.session_id);
                      setIsOpen(false);
                    }}
                    className={`w-full text-left p-4 rounded-xl hover:bg-stone-50 border ${
                      currentSessionId === session.session_id
                        ? 'border-orange-200 bg-orange-50'
                        : 'border-stone-100'
                    }`}
                    data-testid={`history-session-${session.session_id}`}
                  >
                    <p className="text-sm font-medium text-stone-900 mb-1 truncate">
                      {session.preview}
                    </p>
                    <p className="text-xs text-stone-500">
                      {formatTimestamp(session.timestamp)}
                    </p>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
};

export default ChatHistory;
