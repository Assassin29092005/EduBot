import React from 'react';

function MessageBubble({ text, sender }) {
  return (
    <div className={`message-row ${sender}`}>
      <div className={`message-bubble ${sender}`}>{text}</div>
    </div>
  );
}

export default MessageBubble;
