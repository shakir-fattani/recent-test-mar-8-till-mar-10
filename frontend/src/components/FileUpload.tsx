import React from 'react';
import { Card } from 'react-bootstrap';
import DragNdrop from './DragNdrop';

const FileUpload: React.FC = () => {
  // const [selectedFile, setSelectedFile] = useState<File | null>(null);

  // const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
  //   if (event.target.files) {
  //     setSelectedFile(event.target.files[0]);
  //   }
  // };

  // const handleFileUpload = () => {
  //   if (selectedFile) {
  //     // Implement file upload logic here
  //     console.log('Uploading file:', selectedFile.name);
  //   }
  // };

  return (
    <Card style={{ width: '100%', height: '39vh' }}>
      <Card.Body>
        <DragNdrop onFilesSelected={(files) => console.log(files)} />
      </Card.Body>
    </Card>
  );
};

export default FileUpload;
