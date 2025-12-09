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

  const handleRename = async (sessionId, newName) => {
    try {
      await axios.put(`${API}/chat/${sessionId}/rename`, { name: newName });
      setSessions(sessions.map(s => 
        s.session_id === sessionId ? { ...s, name: newName, preview: newName } : s
      ));
      setEditingId(null);
    } catch (error) {
      console.error('Error renaming session:', error);
    }
  };

  const handleDelete = async (sessionId) => {
    if (!window.confirm('Delete this chat?')) return;
    
    try {
      await axios.delete(`${API}/chat/${sessionId}`);
      setSessions(sessions.filter(s => s.session_id !== sessionId));
    } catch (error) {
      console.error('Error deleting session:', error);
    }
  };

  const handleNewChat = () => {
    setIsOpen(false);
    if (onNewChat) onNewChat();
  };

  return (
    <>
      {/* Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed left-4 top-4 z-50 flex items-center gap-2 bg-white border border-stone-200 text-stone-700 rounded-xl shadow-md hover:shadow-lg hover:border-stone-300 px-4 py-2.5"
        data-testid="chat-history-toggle"
      >
        <Menu className="w-5 h-5" />
        <span className="font-medium text-sm hidden md:inline">Chat History</span>
      </button>

      {/* Sidebar */}
      {isOpen && (
        <div className="fixed left-0 top-0 bottom-0 w-80 bg-white border-r border-stone-200 shadow-xl z-40 overflow-y-auto">
          <div className="p-6">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <MessageSquare className="w-6 h-6 text-orange-700" />
                <h2 className="font-serif text-2xl text-stone-900">Chats</h2>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="w-8 h-8 rounded-lg hover:bg-stone-100 flex items-center justify-center"
              >
                <X className="w-5 h-5 text-stone-500" />
              </button>
            </div>

            {/* New Chat Button */}
            <button
              onClick={handleNewChat}
              className="w-full flex items-center gap-3 bg-orange-700 text-white hover:bg-orange-800 rounded-xl px-4 py-3 mb-4 font-medium"
              data-testid="new-chat-button"
            >
              <Plus className="w-5 h-5" />
              <span>New Chat</span>
            </button>

            {loading ? (
              <div className="text-center py-8 text-stone-500">Loading...</div>
            ) : sessions.length === 0 ? (
              <div className="text-center py-8 text-stone-500">No chat history yet</div>
            ) : (
              <div className="space-y-2">
                {sessions.map((session) => (
                  <div
                    key={session.session_id}
                    className={`relative group rounded-xl border ${
                      currentSessionId === session.session_id
                        ? 'border-orange-200 bg-orange-50'
                        : 'border-stone-100 hover:bg-stone-50'
                    }`}
                  >
                    {editingId === session.session_id ? (
                      <div className="p-3">
                        <input
                          type="text"
                          value={editName}
                          onChange={(e) => setEditName(e.target.value)}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') handleRename(session.session_id, editName);
                            if (e.key === 'Escape') setEditingId(null);
                          }}
                          onBlur={() => handleRename(session.session_id, editName)}
                          className="w-full px-2 py-1 text-sm border border-orange-300 rounded focus:outline-none focus:ring-2 focus:ring-orange-500"
                          autoFocus
                        />
                      </div>
                    ) : (
                      <>
                        <button
                          onClick={() => {
                            onSelectSession(session.session_id);
                            setIsOpen(false);
                          }}
                          className="w-full text-left p-4"
                          data-testid={`history-session-${session.session_id}`}
                        >
                          <p className="text-sm font-medium text-stone-900 mb-1 truncate pr-16">
                            {session.name || session.preview}
                          </p>
                          <p className="text-xs text-stone-500">
                            {formatTimestamp(session.timestamp)}
                          </p>
                        </button>
                        
                        {/* Action Buttons */}
                        <div className="absolute right-2 top-2 hidden group-hover:flex gap-1">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setEditingId(session.session_id);
                              setEditName(session.name || session.preview);
                            }}
                            className="p-2 hover:bg-orange-100 rounded-lg"
                            title="Rename"
                          >
                            <Edit2 className="w-3.5 h-3.5 text-orange-700" />
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDelete(session.session_id);
                            }}
                            className="p-2 hover:bg-red-100 rounded-lg"
                            title="Delete"
                          >
                            <Trash2 className="w-3.5 h-3.5 text-red-600" />
                          </button>
                        </div>
                      </>
                    )}
                  </div>
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
