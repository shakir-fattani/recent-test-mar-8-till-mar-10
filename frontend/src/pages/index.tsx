import React, { useState } from 'react';
import ChatInterface from '../components/ChatInterface';
import VNCDisplay from '../components/VNCDisplay';
import FileUpload from '../components/FileUpload';
import TaskHistory from '../components/TaskHistory';
import { Row, Col } from 'react-bootstrap';
import useHolderJs from '../hooks/useHolderJs';
import { FiMaximize, FiMinus, FiX } from 'react-icons/fi';

const Home: React.FC = () => {
  useHolderJs();
  const [chatId, setChatId] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);

  return (
    <div style={{ width: '100%', padding: '2vw' }}>
      <Row style={{ marginBottom: '2vh', height: '6vh' }}>
        <Col xs={3}>
          <img src="holder.js/50x50" />
        </Col>
        <Col xs={6}>
          <center>
            <img src="holder.js/300x50" />
          </center>
        </Col>
        <Col xs={3}>
          <FiX style={{ fontSize: '40px', float: 'inline-end', padding: '.5vw' }} />
          <FiMaximize style={{ fontSize: '40px', float: 'inline-end', padding: '.5vw' }} />
          <FiMinus style={{ fontSize: '40px', float: 'inline-end', padding: '.5vw' }} />
        </Col>
      </Row>
      <Row>
        <TaskHistory
          chatId={chatId}
          loading={loading}
          setLoading={setLoading}
          newChat={() => setChatId('')}
          openExistingChat={setChatId}
        />
        <VNCDisplay
          colSize={6}
          src={
            '//localhost:6080/vnc.html?&resize=scale&autoconnect=1&view_only=1&reconnect=100&reconnect_delay=2000'
          }
        />
        <Col xs={3}>
          <ChatInterface
            loading={loading}
            setLoading={setLoading}
            chatId={chatId}
            setChatId={setChatId}
          />
          <FileUpload />
        </Col>
      </Row>
    </div>
  );
};

export default Home;
