import React from 'react';
import { Button, Card, Col } from 'react-bootstrap';
import { FiMic, FiPause } from 'react-icons/fi';

interface VNCDisplayProps {
  src: string;
  colSize?: number;
}

const VNCDisplay: React.FC<VNCDisplayProps> = ({ src, colSize = 6 }) => {
  return (
    <Col xs={colSize}>
      <Card style={{ width: '100%', height: '84vh' }}>
        <Card.Header>
          <Col style={{ padding: '1vh' }}>
            <Button variant="primary" style={{ float: 'inline-end' }}>
              <FiPause /> Stop
            </Button>
            <Button
              variant="primary"
              style={{ float: 'inline-end', marginLeft: '1vh', marginRight: '1vh' }}
            >
              <FiMic /> Record
            </Button>
          </Col>
        </Card.Header>
        <Card.Body>
          <iframe allowFullScreen={true} src={src} style={{ width: '100%', height: '100%' }} />
        </Card.Body>
      </Card>
    </Col>
  );
};

export default VNCDisplay;
