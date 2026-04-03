import axios from 'axios';

// Dev: leave VITE_API_URL unset so requests go through the Vite proxy (see vite.config.ts).
// Prod / direct: set VITE_API_URL to your Flask base URL, e.g. http://127.0.0.1:5000
const API_URL = import.meta.env.VITE_API_URL ?? '';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Default JSON Content-Type breaks multipart uploads (boundary must be set by the browser).
api.interceptors.request.use((config) => {
  if (config.data instanceof FormData) {
    delete config.headers['Content-Type'];
  }
  return config;
});
