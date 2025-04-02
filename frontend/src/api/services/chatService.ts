import apiClient from '../axiosConfig';
import { Chat, ChatMessage } from '../types/index';

const chatService = {
  createChat: async (initialMessage?: string): Promise<Chat> => {
    const payload = initialMessage ? { initial_message: initialMessage } : {};
    const response = await apiClient.post<Chat>('/chats/', payload);
    return response.data;
  },

  getAllChats: async (): Promise<Chat[]> => {
    const response = await apiClient.get<Chat[]>('/chats/');
    return response.data;
  },

  getChatById: async (chatId: string): Promise<Chat> => {
    const response = await apiClient.get<Chat>(`/chats/${chatId}`);
    return response.data;
  },

  addMessageToChat: async (
    chatId: string,
    role: string,
    message: string,
    extraData = {},
  ): Promise<ChatMessage> => {
    const payload = {
      role,
      message: message,
      extra_data: extraData,
    };
    const response = await apiClient.post<ChatMessage>(`/chats/${chatId}/history`, payload);
    return response.data;
  },

  deleteChat: async (chatId: string): Promise<boolean> => {
    const response = await apiClient.delete<boolean>(`/chats/${chatId}`);
    return response.data;
  },
};

export default chatService;
