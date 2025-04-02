import axios, { AxiosError, AxiosInstance, AxiosResponse } from 'axios';

// Base API client configuration
const apiClient: AxiosInstance = axios.create({
  baseURL: '/api/v1', // This will be routed through the Next.js proxy
  headers: { 'Content-Type': 'application/json' },
  timeout: 600 * 1000, // 600 seconds timeout
});

// Request interceptor for adding auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);

// Response interceptor for handling common errors
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error: AxiosError) => {
    // Handle 401 Unauthorized errors and redirect to login
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }

    // Handle 403 Forbidden errors
    if (error.response && error.response.status === 403) {
      console.error('Permission denied');
      localStorage.removeItem('token');
      window.location.href = '/login';
    }

    // Handle network errors
    if (!error.response) {
      console.error('Network error, please check your connection');
    }

    return Promise.reject(error);
  },
);

export default apiClient;
