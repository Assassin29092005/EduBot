import React, { useState, useCallback, useEffect } from 'react';
import ChatWindow from './components/ChatWindow';
import ChatInput from './components/ChatInput';
import { sendMessage } from './services/lexClient';
import './App.css';

const WELCOME_MESSAGE = {
  text: "Hi! I'm EduBot, your student assistant. I can help you with course syllabi, professor info, class schedules, and assignment deadlines. Try asking me something like \"What is the syllabus for CS101?\"",
  sender: 'bot',
};

const STORAGE_KEY = 'edubot-chat-history';

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

  // Persist messages to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
  }, [messages]);

  const handleSend = useCallback(async (text) => {
    if (!text.trim()) return;

    setMessages((prev) => [...prev, { text, sender: 'user' }]);
    setIsLoading(true);

    try {
      const response = await sendMessage(text);
      setMessages((prev) => [...prev, { text: response, sender: 'bot' }]);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages((prev) => [
        ...prev,
        { text: 'Sorry, something went wrong. Please try again.', sender: 'bot' },
      ]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleClearHistory = useCallback(() => {
    setMessages([WELCOME_MESSAGE]);
    localStorage.removeItem(STORAGE_KEY);
  }, []);

  return (
    <div className="app">
      <header className="app-header">
        <h1>EduBot</h1>
        <p>Student Assistant</p>
        <button className="clear-history-btn" onClick={handleClearHistory}>
          Clear Chat
        </button>
      </header>
      <main className="chat-container">
        <ChatWindow messages={messages} isLoading={isLoading} />
        <ChatInput onSend={handleSend} isLoading={isLoading} />
      </main>
    </div>
  );
}

export default App;
