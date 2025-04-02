import React, { useEffect, useState } from 'react';
import { AiOutlineCheckCircle, AiOutlineCloudUpload } from 'react-icons/ai';
import { MdClear } from 'react-icons/md';
import '../styles/drag-drop.css';

interface DragNdropProps {
  onFilesSelected: (files: File[]) => void;
}

const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

const DragNdrop: React.FC<DragNdropProps> = ({ onFilesSelected }) => {
  const [files, setFiles] = useState<File[]>([]);

  const handleFileChange = (event: React.ChangeEvent) => {
    const selectedFiles = (event.target as HTMLInputElement).files;
    if (!selectedFiles || selectedFiles.length == 0) return;

    const newFiles = Array.from(selectedFiles);
    setFiles((prevFiles) => [...prevFiles, ...newFiles] as File[]);
  };
  const handleDrop = (event: React.DragEvent) => {
    event.preventDefault();
    const droppedFiles = event.dataTransfer!.files;
    if (droppedFiles.length == 0) return;

    const newFiles = Array.from(droppedFiles);
    setFiles((prevFiles) => [...prevFiles, ...newFiles] as File[]);
  };

  const handleRemoveFile = (index: number) => {
    setFiles((prevFiles) => prevFiles.filter((_, i) => i !== index));
  };

  useEffect(() => {
    onFilesSelected(files);
  }, [files, onFilesSelected]);

  return (
    <section className="drag-drop" style={{ width: '100%' }}>
      <div
        className={`document-uploader ${files.length > 0 ? 'upload-box active' : 'upload-box'}`}
        onDrop={handleDrop}
        style={{ width: '100%', minHeight: '35vh' }}
        onDragOver={(event) => event.preventDefault()}
      >
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
            id="browse"
            onChange={handleFileChange}
            accept=".pdf,.docx,.txt,.png,.jpg,.jpeg"
            multiple
          />
        </>

        {files.length > 0 && (
          <div className="file-list">
            <div className="file-list__container">
              {files.map((file, index) => (
                <div className="file-item" key={index}>
                  <div className="file-info">
                    <p
                      title={`${file.name}\nType: ${file.type} \nLast Modified: ${new Date(
                        file.lastModified,
                      ).toLocaleString()} \nSize: ${formatFileSize(file.size)}`}
                    >
                      {file.name}
                    </p>
                  </div>
                  <div className="file-actions">
                    <MdClear onClick={() => handleRemoveFile(index)} />
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
