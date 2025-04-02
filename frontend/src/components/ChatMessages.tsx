import React from 'react';
import { ChatMessage as ChatMessageType } from '@/api/types/index';
import ChatMessage from './ChatMessage';

interface ChatMessagesProps {
  messages: ChatMessageType[];
}

const ChatMessages: React.FC<ChatMessagesProps> = ({ messages }) => {
  if (messages.length == 0)
    return (
      <ChatMessage
        message={{
          id: '1',
          chat_id: '1',
          role: 'assistant',
          message: 'Hi!, Let me know, how can I help you?',
          created_at: '2021-10-01T00:00:00',
          extra_data: {},
        }}
      />
    );

  return (
    <>
      {messages.map((message) => {
        return (
          <ChatMessage
            message={{
              id: message.id,
              chat_id: message.chat_id,
              role: message.role,
              message: message.message,
              created_at: message.created_at,
              extra_data: message.extra_data,
            }}
            key={message.id}
          />
        );
      })}
    </>
  );
};

export default ChatMessages;
