import apiClient from '../axiosConfig';
import { LoginRequest, TokenResponse } from '../types';

const TOKEN_KEY = 'token';

const authService = {
  login: async (credentials: LoginRequest): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>('/auth/login', credentials);

    // Store token on successful login
    if (response.data && response.data.access_token) {
      localStorage.setItem(TOKEN_KEY, response.data.access_token);
    }

    return response.data;
  },

  logout: (): void => {
    localStorage.removeItem(TOKEN_KEY);
    window.location.href = '/login';
  },

  isAuthenticated: (): boolean => {
    return !!localStorage.getItem(TOKEN_KEY);
  },
};

export default authService;
