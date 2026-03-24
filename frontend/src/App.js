import React, { useState, useCallback, useEffect } from 'react';
import ChatWindow from './components/ChatWindow';
import ChatInput from './components/ChatInput';
import { sendMessage } from './services/lexClient';
import './App.css';

const STORAGE_KEY = 'edubot-chat-history';

function getTimestamp() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

const WELCOME_MESSAGE = {
  text: "Hi! I'm EduBot, your student assistant. I can help you with course syllabi, professor info, class schedules, and assignment deadlines.\n\nTry asking me something like \"What is the syllabus for CS101?\"",
  sender: 'bot',
  timestamp: getTimestamp(),
};

const QUICK_ACTIONS = [
  'Syllabus for CS101',
  'Who teaches MATH201?',
  'Schedule for PHYS150',
  'Deadlines for BIO101',
];

function loadHistory() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      const parsed = JSON.parse(saved);
      if (Array.isArray(parsed) && parsed.length > 0) return parsed;
    }
  } catch (e) {
    // Corrupted data, ignore
  }
  return [WELCOME_MESSAGE];
}

function App() {
  const [messages, setMessages] = useState(loadHistory);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
  }, [messages]);

  const handleSend = useCallback(async (text) => {
    if (!text.trim()) return;

    const userMsg = { text, sender: 'user', timestamp: getTimestamp() };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const response = await sendMessage(text);
      const botMsg = { text: response, sender: 'bot', timestamp: getTimestamp() };
      setMessages((prev) => [...prev, botMsg]);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages((prev) => [
        ...prev,
        { text: 'Sorry, something went wrong. Please try again.', sender: 'bot', timestamp: getTimestamp() },
      ]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleClearHistory = useCallback(() => {
    const fresh = { ...WELCOME_MESSAGE, timestamp: getTimestamp() };
    setMessages([fresh]);
    localStorage.removeItem(STORAGE_KEY);
  }, []);

  const showQuickActions = messages.length <= 1;

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <span className="header-icon" role="img" aria-label="graduation cap">🎓</span>
          <div>
            <h1>EduBot</h1>
            <p>Student Assistant</p>
          </div>
        </div>
        <button className="clear-history-btn" onClick={handleClearHistory}>
          Clear Chat
        </button>
      </header>
      <main className="chat-container">
        <ChatWindow messages={messages} isLoading={isLoading} />
        {showQuickActions && (
          <div className="quick-actions">
            {QUICK_ACTIONS.map((action) => (
              <button
                key={action}
                className="quick-action-btn"
                onClick={() => handleSend(action)}
                disabled={isLoading}
              >
                {action}
              </button>
            ))}
          </div>
        )}
        <ChatInput onSend={handleSend} isLoading={isLoading} />
      </main>
    </div>
  );
}

export default App;
