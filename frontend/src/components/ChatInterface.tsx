import chatService from '@/api/services/chatService';
import React, { FC, useCallback, useEffect, useState } from 'react';
import { Card, Form, InputGroup } from 'react-bootstrap';
import { FiSend } from 'react-icons/fi';
import ChatMessages from './ChatMessages';
import { Chat } from '../api/types/index';

interface ChatInterfaceProps {
  chatId: string;
  setChatId: (chatId: string) => void;
  loading: boolean;
  setLoading: (loading: boolean) => void;
}

const ChatInterface: FC<ChatInterfaceProps> = ({ chatId, setChatId, setLoading, loading }) => {
  const [refreshCount, setRefreshCount] = useState<number>(0);
  const [prompt, setPrompt] = useState<string>('');
  const [chat, setChat] = useState<Chat>();

  const fetchMessages = useCallback(async () => {
    setLoading(true);
    try {
      const localChat = await chatService.getChatById(chatId);
      setChat(localChat);
    } catch (e) {
      console.error('Failed to fetch chat messages', e);
    }
    setLoading(false);
  }, [chatId, setLoading]);

  useEffect(() => {
    fetchMessages();
  }, [chatId, refreshCount]);

  const sendNewMessage = useCallback(() => {
    setLoading(true);

    if (chatId == '') {
      chatService
        .createChat(prompt)
        .then((res) => {
          if (res.chat_id) setChatId(res.chat_id);
          setPrompt('');
        })
        .catch((e) => {
          console.error('Failed to send message', e);
        })
        .finally(() => {
          setLoading(false);
          setRefreshCount(Date.now());
        });
      return;
    }

    chatService
      .addMessageToChat(chatId, 'user', prompt, {})
      .then(() => {})
      .catch((e) => {
        console.error('Failed to send message', e);
      })
      .finally(() => {
        setLoading(false);
        setPrompt('');
        setRefreshCount(Date.now());
      });
  }, [setLoading, chatId, prompt, setChatId, setPrompt, setRefreshCount]);

  return (
    <Card style={{ width: '100%', height: '43vh', marginBottom: '2vh' }}>
      <Card.Body style={{ height: '100%', overflowY: 'auto' }}>
        <ChatMessages messages={chat?.history || []} />
      </Card.Body>
      <Card.Footer>
        <InputGroup>
          <Form.Control
            aria-label="Write a message"
            value={prompt}
            disabled={loading}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Write a message"
          />
          <InputGroup.Text aria-disabled={loading} onClick={() => sendNewMessage()}>
            <FiSend />
          </InputGroup.Text>
        </InputGroup>
      </Card.Footer>
    </Card>
  );
};

export default ChatInterface;
