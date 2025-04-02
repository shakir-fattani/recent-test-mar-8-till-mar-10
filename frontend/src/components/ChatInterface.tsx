import React, { useState } from 'react';
import { Card, Form, Button, InputGroup } from 'react-bootstrap';
import { FiSend } from 'react-icons/fi';

interface Message {
  id: number;
  content: string;
  sender: 'user' | 'ai';
}

const ChatInterface: React.FC = () => {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    { id: 1, content: 'Hello! How can I help you today?', sender: 'ai' },
    { id: 2, content: 'I need help creating a spreadsheet', sender: 'user' },
    { id: 3, content: 'I need help creating a spreadsheet', sender: 'user' },
    { id: 4, content: 'I need help creating a spreadsheet', sender: 'user' },
    { id: 5, content: 'I need help creating a spreadsheet', sender: 'user' },
    { id: 6, content: 'I need help creating a spreadsheet', sender: 'user' },
    { id: 7, content: 'I need help creating a spreadsheet', sender: 'user' },
  ]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim()) return;

    // Add user message
    const userMessage: Message = {
      id: messages.length + 1,
      content: message,
      sender: 'user',
    };

    setMessages([...messages, userMessage]);
    setMessage('');

    // Mock AI response - replace with actual API call
    setTimeout(() => {
      const aiMessage: Message = {
        id: messages.length + 2,
        content: "I'll help you create a spreadsheet. What kind of data will it contain?",
        sender: 'ai',
      };
      setMessages((prev) => [...prev, aiMessage]);
    }, 1000);
  };

  return (
    <Card className="shadow-sm" style={{ width: '100%', height: '43vh', marginBottom: '2vh' }}>
      <Card.Body className="p-0" style={{ overflow: 'auto', height: '100%' }}>
        {messages.map((msg) => (
          <div className="chat-item shadow-sm" key={msg.id}>
            <img
              src="holder.js/50x50"
              className="chat-avatar"
              title={msg.sender}
              alt={msg.sender}
            />
            <p className="chat-text mb-0">{msg.content}</p>
          </div>
        ))}
      </Card.Body>
      <Card.Footer className="p-2">
        <Form onSubmit={handleSubmit}>
          <InputGroup>
            <Form.Control
              placeholder="Type your message..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
            />
            <Button type="submit" variant="primary">
              <FiSend />
            </Button>
          </InputGroup>
        </Form>
      </Card.Footer>
    </Card>
  );
};

export default ChatInterface;
