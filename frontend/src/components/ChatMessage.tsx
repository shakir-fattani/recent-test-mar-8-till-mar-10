import React from 'react';
import { ChatMessage as ChatMessageType } from '@/api/types/index';
import useHolderJs from '../hooks/useHolderJs';

interface ChatMessageProps {
  message: ChatMessageType;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user';
  useHolderJs();
  const isTool = message.message == 'tool';
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const source = (message.extra_data as unknown as any)?.content?.source || {};
  return (
    <div className="chat-item">
      <img
        className="chat-avatar"
        src={message.role == 'user' ? 'holder.js/50x50' : 'holder.js/50x50'}
        alt={isUser ? 'User Avatar' : 'Assistant Avatar'}
      />
      <div className="chat-text">
        {/* {JSON.stringify(message.extra_data?.content?.source)} */}
        {!isTool ? (
          message.message
        ) : (
          <img
            src={`data:${source.media_type};${source.type},${source.data}`}
            style={{ width: '10vw' }}
          />
        )}
      </div>
    </div>
  );
};

export default ChatMessage;
