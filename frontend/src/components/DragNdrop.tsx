import React, { useCallback } from 'react';
import { AiOutlineCheckCircle, AiOutlineCloudUpload } from 'react-icons/ai';
import { MdClear } from 'react-icons/md';
import '../styles/drag-drop.css';
import { Spinner } from 'react-bootstrap';

interface DragNdropProps {
  files: FileObj[];
  loading: boolean;
  onNewFile: (files: FileObj) => void;
  onFileDelete: (id: string) => void;
}

export interface FileObj {
  id: string;
  name: string;
  file?: File; // in-case of local file
  size: number;
  type: string;
  lastModified: string;
  checksum?: string; // in-case of remote file
  status: string;
}

const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

const DragNdrop: React.FC<DragNdropProps> = ({ loading, files, onNewFile, onFileDelete }) => {
  const handleFileChange = useCallback(
    (event: React.ChangeEvent) => {
      event.preventDefault();
      if (loading) {
        alert('Please wait for the file to be processed');
        return;
      }

      const selectedFiles = (event.target as HTMLInputElement).files;
      if (!selectedFiles || selectedFiles.length == 0) return;

      if (selectedFiles.length != 1) {
        alert('only single file at a time');
        return;
      }

      const file = Array.from(selectedFiles)[0];
      onNewFile({
        id: Date.now() + '',
        name: file.name,
        file,
        size: file.size,
        type: file.type,
        checksum: undefined,
        status: 'uploading',
        lastModified: file.lastModified + '',
      });
    },
    [loading],
  );
  const handleDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();
      if (loading) {
        alert('Please wait for the file to be processed');
        return;
      }

      const droppedFiles = event.dataTransfer!.files;
      if (droppedFiles.length == 0) return;
      if (droppedFiles.length != 1) {
        alert('only single file at a time');
        return;
      }
      const file = Array.from(droppedFiles)[0];
      onNewFile({
        id: Date.now() + '',
        name: file.name,
        file,
        size: file.size,
        type: file.type,
        checksum: undefined,
        status: 'uploading',
        lastModified: file.lastModified + '',
      });
    },
    [loading],
  );

  const handleRemoveFile = useCallback(
    (index: string) => {
      if (loading) {
        alert('Please wait for the file to be processed');
        return;
      }
      onFileDelete(index);
    },
    [loading],
  );

  return (
    <section className="drag-drop" style={{ width: '100%' }}>
      <div
        className={`document-uploader ${files.length > 0 ? 'upload-box active' : 'upload-box'}`}
        onDrop={handleDrop}
        style={{ width: '100%', minHeight: '35vh' }}
        onDragOver={(event) => event.preventDefault()}
      >
        {!loading ? (
          <>
            <AiOutlineCloudUpload
              style={{ fontSize: '60px', paddingTop: '1vh', paddingBottom: '1vh' }}
            />
            <div className="upload-info">
              <div>
                <center>
                  <label htmlFor="browse" className="browse-btn">
                    Drag and drop a single file here or click to select file
                  </label>
                </center>
              </div>
            </div>
            <input
              type="file"
              hidden
              key={files.length}
              id="browse"
              onChange={handleFileChange}
              accept=".pdf,.docx,.txt,.png,.jpg,.jpeg"
              multiple={false}
            />
          </>
        ) : (
          <Spinner as="span" animation="border" role="status" aria-hidden="true" />
        )}

        {files.length > 0 && (
          <div className="file-list">
            <div className="file-list__container">
              {files.map((file, index) => (
                <div className="file-item" key={index}>
                  <div className="file-info">
                    <p
                      title={`${file.name} - ${file.status}\nType: ${
                        file.type
                      } \nLast Modified: ${new Date(
                        file.lastModified,
                      ).toLocaleString()} \nSize: ${formatFileSize(parseInt(file.size + ''))}`}
                    >
                      {file.name}
                    </p>
                  </div>
                  <div className="file-actions">
                    <MdClear onClick={() => handleRemoveFile(file.id)} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {files.length > 0 && (
          <div className="success-file">
            <AiOutlineCheckCircle style={{ color: '#6DC24B', marginRight: 1 }} />
            <p>{files.length} file(s) selected</p>
          </div>
        )}
      </div>
    </section>
  );
};

export default DragNdrop;
