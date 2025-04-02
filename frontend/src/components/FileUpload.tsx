import React, { useCallback, useEffect, useState } from 'react';
import { Card } from 'react-bootstrap';
import DragNdrop, { FileObj } from './DragNdrop';
import fileService from '@/api/services/fileService';

const FileUpload: React.FC = () => {
  const [refreshCount, setRefreshCount] = useState<number>(0);
  const [files, setFiles] = useState<FileObj[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const getFilesList = useCallback(async () => {
    try {
      setLoading(true);
      const files = await fileService.getAllFiles();
      setFiles(
        files.map<FileObj>((file) => {
          return {
            id: file.id,
            name: file.file_name,
            size: file.file_size,
            type: file.file_type,
            checksum: file.file_checksum,
            status: 'remote',
          } as unknown as FileObj;
        }),
      );
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  }, [setFiles, setLoading]);

  useEffect(() => {
    getFilesList();
  }, [refreshCount]);

  const onNewFile = useCallback(
    async (file: FileObj) => {
      const newFiles = {
        id: Date.now(),
        name: file.name,
        file,
        size: file.size,
        type: file.type,
        checksum: null,
        status: 'local',
      } as unknown as FileObj;
      setFiles([...files, newFiles]);

      // upload file
      setLoading(true);
      await fileService.uploadFile(file.file!).catch(console.error);
      setRefreshCount(Date.now());
    },
    [setRefreshCount, setLoading],
  );

  const onFileDelete = useCallback(
    async (fileId: string) => {
      setLoading(true);
      await fileService.deleteFile(fileId).catch(console.error);
      setRefreshCount(Date.now());
    },
    [setRefreshCount, setLoading],
  );

  return (
    <Card style={{ width: '100%', height: '39vh' }}>
      <Card.Body>
        <DragNdrop
          loading={loading}
          files={files}
          onNewFile={onNewFile}
          onFileDelete={onFileDelete}
        />
      </Card.Body>
    </Card>
  );
};

export default FileUpload;
