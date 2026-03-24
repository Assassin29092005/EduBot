import React from 'react';

function MessageBubble({ text, sender, timestamp }) {
  return (
    <div className={`message-row ${sender}`}>
      {sender === 'bot' && (
        <div className="bot-avatar" title="EduBot">
          <span role="img" aria-label="bot">🎓</span>
        </div>
      )}
      <div>
        <div className={`message-bubble ${sender}`}>{text}</div>
        {timestamp && <div className="message-timestamp">{timestamp}</div>}
      </div>
    </div>
  );
}

export default MessageBubble;
