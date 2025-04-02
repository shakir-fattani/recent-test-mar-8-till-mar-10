import apiClient from '../axiosConfig';
import { FileInfo } from '../types';

const fileService = {
  uploadFile: async (file: File): Promise<FileInfo> => {
    const formData = new FormData();
    formData.append('file', file);

    // Special headers for file upload
    const response = await apiClient.post<FileInfo>('/files/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  getAllFiles: async (): Promise<FileInfo[]> => {
    const response = await apiClient.get<FileInfo[]>('/files/');
    return response.data;
  },

  getFileById: async (fileId: string): Promise<Blob> => {
    const response = await apiClient.get<Blob>(`/files/${fileId}`, {
      responseType: 'blob',
    });
    return response.data;
  },

  deleteFile: async (fileId: string): Promise<boolean> => {
    const response = await apiClient.delete<boolean>(`/files/${fileId}`);
    return response.data;
  },
};

export default fileService;
