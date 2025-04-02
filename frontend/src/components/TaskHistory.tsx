import React from 'react';
import { Button, Card, Col, Form, InputGroup } from 'react-bootstrap';
import { FiSearch } from 'react-icons/fi';

interface TaskHistoryProps {
  colSize?: number;
}

const TaskHistory: React.FC<TaskHistoryProps> = ({ colSize = 3 }) => {
  return (
    <Col xs={colSize}>
      <InputGroup className="mb-3" style={{ width: '100%', height: '5vh' }}>
        <InputGroup.Text id="basic-addon1">
          <FiSearch />
        </InputGroup.Text>
        <Form.Control placeholder="Search" aria-label="search" aria-describedby="basic-addon1" />
      </InputGroup>
      <Card style={{ width: '100%', height: '70vh', marginBottom: '2vh', marginTop: '2vh' }}>
        <Card.Header>
          <Card.Title>
            <center>Task History</center>
          </Card.Title>
        </Card.Header>
        <Card.Body></Card.Body>
      </Card>
      <Button variant="primary" style={{ width: '100%', height: '5vh' }}>
        New Agent Task
      </Button>
    </Col>
  );
};

export default TaskHistory;
