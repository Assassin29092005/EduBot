import React, { useState, useCallback } from 'react';
import ChatWindow from './components/ChatWindow';
import ChatInput from './components/ChatInput';
import { sendMessage } from './services/lexClient';
import './App.css';

function App() {
  const [messages, setMessages] = useState([
    {
      text: "Hi! I'm EduBot, your student assistant. I can help you with course syllabi, professor info, class schedules, and assignment deadlines. Try asking me something like \"What is the syllabus for CS101?\"",
      sender: 'bot',
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);

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

  return (
    <div className="app">
      <header className="app-header">
        <h1>EduBot</h1>
        <p>Student Assistant</p>
      </header>
      <main className="chat-container">
        <ChatWindow messages={messages} isLoading={isLoading} />
        <ChatInput onSend={handleSend} isLoading={isLoading} />
      </main>
    </div>
  );
}

export default App;
