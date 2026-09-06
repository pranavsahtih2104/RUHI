import React, { useState, useEffect } from 'react';
import { 
  Brain, Search, Plus, Trash2, Edit3, Check, X, Shield, RefreshCw, AlertCircle, Sparkles, Tag 
} from 'lucide-react';
import { fetchMemories, createMemory, updateMemory, deleteMemory } from '../services/api';

const MEMORY_TYPES = [
  { id: 'all', label: 'All Memories' },
  { id: 'preference', label: 'Preferences' },
  { id: 'project', label: 'Projects' },
  { id: 'goal', label: 'Goals' },
  { id: 'fact', label: 'Facts' },
  { id: 'instruction', label: 'Instructions' },
  { id: 'general', label: 'General' },
];

export default function MemoryModal({ isOpen, onClose }) {
  const [memories, setMemories] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedType, setSelectedType] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  
  // New memory form state
  const [isAdding, setIsAdding] = useState(false);
  const [newContent, setNewContent] = useState('');
  const [newType, setNewType] = useState('preference');
  const [newImportance, setNewImportance] = useState(7);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Edit memory state
  const [editingId, setEditingId] = useState(null);
  const [editContent, setEditContent] = useState('');
  const [editType, setEditType] = useState('general');
  const [editImportance, setEditImportance] = useState(5);

  const loadMemories = async () => {
    setIsLoading(true);
    try {
      const data = await fetchMemories({
        type: selectedType,
        search: searchQuery,
        active: true,
      });
      setMemories(data.memories || []);
      setTotalCount(data.total || 0);
    } catch (err) {
      console.error('Error loading memories:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      loadMemories();
    }
  }, [isOpen, selectedType, searchQuery]);

  if (!isOpen) return null;

  const handleCreateMemory = async (e) => {
    e.preventDefault();
    if (!newContent.trim()) return;

    setIsSubmitting(true);
    try {
      await createMemory({
        content: newContent.trim(),
        memory_type: newType,
        importance: parseInt(newImportance, 10),
      });
      setNewContent('');
      setIsAdding(false);
      await loadMemories();
    } catch (err) {
      console.error('Error creating memory:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleStartEdit = (mem) => {
    setEditingId(mem.id);
    setEditContent(mem.content);
    setEditType(mem.memory_type);
    setEditImportance(mem.importance);
  };

  const handleSaveEdit = async (memId) => {
    if (!editContent.trim()) return;
    try {
      await updateMemory(memId, {
        content: editContent.trim(),
        memory_type: editType,
        importance: parseInt(editImportance, 10),
      });
      setEditingId(null);
      await loadMemories();
    } catch (err) {
      console.error('Error updating memory:', err);
    }
  };

  const handleDeleteMemory = async (memId) => {
    try {
      await deleteMemory(memId);
      await loadMemories();
    } catch (err) {
      console.error('Error deleting memory:', err);
    }
  };

  const getTypeBadgeClass = (type) => {
    switch (type) {
      case 'preference': return 'badge-preference';
      case 'project': return 'badge-project';
      case 'goal': return 'badge-goal';
      case 'instruction': return 'badge-instruction';
      case 'fact': return 'badge-fact';
      default: return 'badge-general';
    }
  };

  return (
    <div className="memory-modal-overlay" onClick={onClose}>
      <div className="memory-modal-content" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="memory-modal-header">
          <div className="memory-header-title">
            <div className="memory-icon-glow">
              <Brain size={20} color="var(--cyan-primary)" />
            </div>
            <div>
              <h3>RUHI Persistent Memory</h3>
              <p>Knowledge and preferences retained across conversations ({totalCount} active)</p>
            </div>
          </div>

          <div className="memory-header-actions">
            <button
              onClick={() => setIsAdding(!isAdding)}
              className={`btn-add-memory ${isAdding ? 'active' : ''}`}
            >
              <Plus size={14} />
              <span>{isAdding ? 'Cancel' : 'Add Memory'}</span>
            </button>

            <button onClick={onClose} className="btn-modal-close" aria-label="Close memory modal">
              <X size={18} />
            </button>
          </div>
        </div>

        {/* Add Memory Panel */}
        {isAdding && (
          <form className="add-memory-panel" onSubmit={handleCreateMemory}>
            <h4>Record New Persistent Memory</h4>
            <textarea
              value={newContent}
              onChange={(e) => setNewContent(e.target.value)}
              placeholder="e.g., I prefer dark UI interfaces and concise code explanations."
              className="memory-textarea"
              rows={3}
              autoFocus
            />

            <div className="add-memory-controls">
              <div className="control-field">
                <label>Memory Type</label>
                <select
                  value={newType}
                  onChange={(e) => setNewType(e.target.value)}
                  className="memory-select"
                >
                  <option value="preference">Preference</option>
                  <option value="project">Project</option>
                  <option value="goal">Goal</option>
                  <option value="fact">Fact</option>
                  <option value="instruction">Instruction</option>
                  <option value="general">General</option>
                </select>
              </div>

              <div className="control-field">
                <label>Importance (1 - 10): <strong>{newImportance}</strong></label>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={newImportance}
                  onChange={(e) => setNewImportance(e.target.value)}
                  className="memory-slider"
                />
              </div>

              <button
                type="submit"
                disabled={!newContent.trim() || isSubmitting}
                className="btn-save-new-memory"
              >
                {isSubmitting ? 'Saving...' : 'Save to RUHI'}
              </button>
            </div>
          </form>
        )}

        {/* Search & Filters */}
        <div className="memory-filter-bar">
          <div className="memory-search-wrapper">
            <Search size={14} color="var(--text-tertiary)" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search memories..."
              className="memory-search-input"
            />
            {searchQuery && (
              <button onClick={() => setSearchQuery('')} className="btn-search-clear">
                <X size={12} />
              </button>
            )}
          </div>

          <div className="memory-type-pills">
            {MEMORY_TYPES.map((t) => (
              <button
                key={t.id}
                onClick={() => setSelectedType(t.id)}
                className={`type-pill-btn ${selectedType === t.id ? 'active' : ''}`}
              >
                {t.label}
              </button>
            ))}
          </div>
        </div>

        {/* Memories List */}
        <div className="memory-items-container">
          {isLoading ? (
            <div className="memory-loading-state">
              <RefreshCw size={20} className="spin-icon" color="var(--cyan-primary)" />
              <span>Loading persistent memories from PostgreSQL...</span>
            </div>
          ) : memories.length === 0 ? (
            <div className="memory-empty-state">
              <Brain size={36} color="var(--text-tertiary)" />
              <h4>No persistent memories found</h4>
              <p>
                {searchQuery || selectedType !== 'all'
                  ? 'Try adjusting your search query or category filter.'
                  : 'RUHI automatically stores important project context and preferences when you chat or say "Remember that...".'}
              </p>
            </div>
          ) : (
            memories.map((mem) => (
              <div key={mem.id} className="memory-card">
                {editingId === mem.id ? (
                  <div className="memory-edit-view">
                    <textarea
                      value={editContent}
                      onChange={(e) => setEditContent(e.target.value)}
                      className="memory-textarea"
                      rows={3}
                    />
                    <div className="memory-edit-footer">
                      <select
                        value={editType}
                        onChange={(e) => setEditType(e.target.value)}
                        className="memory-select"
                      >
                        <option value="preference">Preference</option>
                        <option value="project">Project</option>
                        <option value="goal">Goal</option>
                        <option value="fact">Fact</option>
                        <option value="instruction">Instruction</option>
                        <option value="general">General</option>
                      </select>

                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ fontSize: '0.78rem', color: 'var(--text-tertiary)' }}>
                          Score: {editImportance}
                        </span>
                        <input
                          type="range"
                          min="1"
                          max="10"
                          value={editImportance}
                          onChange={(e) => setEditImportance(e.target.value)}
                          className="memory-slider"
                          style={{ width: '80px' }}
                        />
                      </div>

                      <div style={{ display: 'flex', gap: '6px' }}>
                        <button
                          onClick={() => handleSaveEdit(mem.id)}
                          className="btn-card-save"
                          title="Save changes"
                        >
                          <Check size={13} />
                          <span>Save</span>
                        </button>
                        <button
                          onClick={() => setEditingId(null)}
                          className="btn-card-cancel"
                          title="Cancel edit"
                        >
                          <X size={13} />
                        </button>
                      </div>
                    </div>
                  </div>
                ) : (
                  <>
                    <div className="memory-card-body">
                      <p className="memory-card-text">{mem.content}</p>
                      <div className="memory-card-meta">
                        <span className={`memory-type-badge ${getTypeBadgeClass(mem.memory_type)}`}>
                          <Tag size={10} />
                          {mem.memory_type}
                        </span>
                        <span className="memory-importance-pill" title="Importance score (1-10)">
                          Importance: {mem.importance}/10
                        </span>
                        <span className="memory-source-tag">
                          Source: {mem.source}
                        </span>
                        <span className="memory-date">
                          {new Date(mem.created_at).toLocaleDateString(undefined, {
                            month: 'short',
                            day: 'numeric',
                            year: 'numeric',
                          })}
                        </span>
                      </div>
                    </div>

                    <div className="memory-card-tools">
                      <button
                        onClick={() => handleStartEdit(mem)}
                        className="btn-mem-action edit"
                        title="Edit memory"
                      >
                        <Edit3 size={13} />
                      </button>
                      <button
                        onClick={() => {
                          if (confirm(`Remove this persistent memory: "${mem.content}"?`)) {
                            handleDeleteMemory(mem.id);
                          }
                        }}
                        className="btn-mem-action delete"
                        title="Delete memory"
                      >
                        <Trash2 size={13} />
                      </button>
                    </div>
                  </>
                )}
              </div>
            ))
          )}
        </div>

        {/* Footer */}
        <div className="memory-modal-footer">
          <div className="memory-privacy-notice">
            <Shield size={13} color="var(--cyan-primary)" />
            <span>Stored securely in your local PostgreSQL database (<code>ruhi-web</code>). Never transmitted to third-party databases.</span>
          </div>
          <button onClick={onClose} className="btn-modal-done">
            Done
          </button>
        </div>
      </div>
    </div>
  );
}
