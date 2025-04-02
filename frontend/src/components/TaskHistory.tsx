import chatService from '@/api/services/chatService';
import React, { ChangeEvent, FC, useCallback, useEffect, useState } from 'react';
import { Button, Card, Col, Form, InputGroup, ListGroup } from 'react-bootstrap';
import { FiMessageCircle, FiSearch } from 'react-icons/fi';
import { Chat } from '../api/types/index';

interface TaskHistoryProps {
  colSize?: number;
  loading: boolean;
  setLoading: (loading: boolean) => void;
  newChat: () => void;
  openExistingChat: (chatId: string) => void;
  chatId: string;
}

const TaskHistory: FC<TaskHistoryProps> = ({
  colSize = 3,
  newChat,
  chatId,
  openExistingChat,
  loading,
  setLoading,
}) => {
  const [randomNo, setRandomNo] = useState<number>(0);
  const [searchText, setSearchText] = useState<string>('');
  const [chats, setChats] = useState<Chat[]>([]);

  const fetchChats = useCallback(async () => {
    setLoading(true);
    try {
      const chats = await chatService.getAllChats();
      setChats(chats);
    } catch (e) {
      console.error('Failed to fetch chat messages', e);
    }
    setLoading(false);
  }, [setLoading, setChats]);

  useEffect(() => {
    setRandomNo(Date.now());
  }, [chatId]);

  useEffect(() => {
    fetchChats();
  }, [chatId, randomNo]);

  return (
    <Col xs={colSize}>
      <InputGroup className="mb-3" style={{ width: '100%', height: '5vh' }}>
        <InputGroup.Text id="basic-addon1">
          <FiSearch />
        </InputGroup.Text>
        <Form.Control
          placeholder="Search"
          value={searchText}
          disabled={loading}
          onChange={(e: ChangeEvent<HTMLInputElement>) => setSearchText(e.target.value)}
          aria-label="search"
          aria-describedby="basic-addon1"
        />
      </InputGroup>
      <Card style={{ width: '100%', height: '70vh', marginBottom: '2vh', marginTop: '2vh' }}>
        <Card.Header>
          <Card.Title>
            <center>Task History</center>
          </Card.Title>
        </Card.Header>
        <Card.Body style={{ overflowY: 'scroll', height: '100%' }}>
          <ListGroup>
            {chats
              .filter((chat) =>
                chat.first_message?.toLowerCase().includes(searchText.toLowerCase()),
              )
              .map((chat) => (
                <ListGroup.Item
                  key={chat.chat_id}
                  action={!loading}
                  onClick={() => openExistingChat(chat.chat_id)}
                >
                  <FiMessageCircle /> {chat.first_message}
                </ListGroup.Item>
              ))}
          </ListGroup>
        </Card.Body>
      </Card>
      <Button
        variant="primary"
        disabled={loading}
        onClick={newChat}
        style={{ width: '100%', height: '5vh' }}
      >
        New Agent Task
      </Button>
    </Col>
  );
};

export default TaskHistory;
