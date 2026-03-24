import React, { useState } from 'react';

function ChatInput({ onSend, isLoading }) {
  const [text, setText] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (text.trim() && !isLoading) {
      onSend(text);
      setText('');
    }
  };

  return (
    <form className="chat-input" onSubmit={handleSubmit}>
      <input
        type="text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Ask me about courses, professors, schedules..."
        disabled={isLoading}
      />
      <button type="submit" disabled={isLoading || !text.trim()}>
        Send
      </button>
    </form>
  );
}

export default ChatInput;
