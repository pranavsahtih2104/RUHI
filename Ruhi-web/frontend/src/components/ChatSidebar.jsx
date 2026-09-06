import React, { useState } from 'react';
import { 
  Plus, MessageSquare, Trash2, Edit2, Check, X, ChevronLeft, ChevronRight, Clock 
} from 'lucide-react';

export default function ChatSidebar({
  isOpen,
  onToggle,
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewConversation,
  onRenameConversation,
  onDeleteConversation,
}) {
  const [editingId, setEditingId] = useState(null);
  const [editTitle, setEditTitle] = useState('');

  const startRename = (conv, e) => {
    e.stopPropagation();
    setEditingId(conv.id);
    setEditTitle(conv.title);
  };

  const handleSaveRename = (convId, e) => {
    e.stopPropagation();
    if (editTitle.trim()) {
      onRenameConversation(convId, editTitle.trim());
    }
    setEditingId(null);
  };

  const handleCancelRename = (e) => {
    e.stopPropagation();
    setEditingId(null);
  };

  // Group conversations: Today, Yesterday, Older
  const groupConversations = () => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    const groups = {
      today: [],
      yesterday: [],
      older: [],
    };

    conversations.forEach((conv) => {
      const convDate = new Date(conv.updated_at || conv.created_at);
      convDate.setHours(0, 0, 0, 0);

      if (convDate.getTime() === today.getTime()) {
        groups.today.push(conv);
      } else if (convDate.getTime() === yesterday.getTime()) {
        groups.yesterday.push(conv);
      } else {
        groups.older.push(conv);
      }
    });

    return groups;
  };

  const groups = groupConversations();

  return (
    <aside className={`chat-sidebar ${isOpen ? 'open' : 'collapsed'}`}>
      <div className="sidebar-header">
        <button 
          onClick={onNewConversation}
          className="btn-new-chat"
          title="Start a new conversation"
        >
          <Plus size={15} />
          <span>New Conversation</span>
        </button>

        <button 
          onClick={onToggle}
          className="btn-sidebar-toggle"
          title={isOpen ? 'Collapse history' : 'Expand history'}
          aria-label="Toggle chat history sidebar"
        >
          {isOpen ? <ChevronLeft size={16} /> : <ChevronRight size={16} />}
        </button>
      </div>

      <div className="sidebar-history-scroll">
        {conversations.length === 0 ? (
          <div className="sidebar-empty-state">
            <Clock size={20} color="var(--text-tertiary)" />
            <span>No previous conversations yet</span>
          </div>
        ) : (
          <>
            {groups.today.length > 0 && (
              <div className="history-group">
                <div className="history-group-label">Today</div>
                {groups.today.map((conv) => renderItem(conv))}
              </div>
            )}

            {groups.yesterday.length > 0 && (
              <div className="history-group">
                <div className="history-group-label">Yesterday</div>
                {groups.yesterday.map((conv) => renderItem(conv))}
              </div>
            )}

            {groups.older.length > 0 && (
              <div className="history-group">
                <div className="history-group-label">Previous</div>
                {groups.older.map((conv) => renderItem(conv))}
              </div>
            )}
          </>
        )}
      </div>
    </aside>
  );

  function renderItem(conv) {
    const isActive = conv.id === activeConversationId;
    const isEditing = editingId === conv.id;

    return (
      <div
        key={conv.id}
        onClick={() => !isEditing && onSelectConversation(conv.id)}
        className={`history-item ${isActive ? 'active' : ''}`}
        title={conv.title}
      >
        <MessageSquare size={14} className="history-icon" />

        {isEditing ? (
          <div className="history-edit-box" onClick={(e) => e.stopPropagation()}>
            <input
              type="text"
              value={editTitle}
              onChange={(e) => setEditTitle(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleSaveRename(conv.id, e);
                if (e.key === 'Escape') handleCancelRename(e);
              }}
              autoFocus
              className="history-rename-input"
            />
            <button 
              onClick={(e) => handleSaveRename(conv.id, e)}
              className="btn-history-action save"
              title="Save title"
            >
              <Check size={12} />
            </button>
            <button 
              onClick={handleCancelRename}
              className="btn-history-action cancel"
              title="Cancel"
            >
              <X size={12} />
            </button>
          </div>
        ) : (
          <>
            <span className="history-title">{conv.title}</span>
            <div className="history-actions" onClick={(e) => e.stopPropagation()}>
              <button 
                onClick={(e) => startRename(conv, e)}
                className="btn-history-tool"
                title="Rename conversation"
                aria-label="Rename conversation"
              >
                <Edit2 size={12} />
              </button>
              <button 
                onClick={(e) => {
                  e.stopPropagation();
                  if (confirm(`Delete conversation "${conv.title}"?`)) {
                    onDeleteConversation(conv.id);
                  }
                }}
                className="btn-history-tool delete"
                title="Delete conversation"
                aria-label="Delete conversation"
              >
                <Trash2 size={12} />
              </button>
            </div>
          </>
        )}
      </div>
    );
  }
}
