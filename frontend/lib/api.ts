/**
 * Axios API client with JWT interceptor.
 * All API calls go through this instance.
 */

import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 30000,
});

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Handle 401 globally — redirect to login
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== "undefined") {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export default api;

// ─── Auth ─────────────────────────────────────────────────────────────────────

export const authAPI = {
  signup: (data: { name: string; email: string; password: string }) =>
    api.post("/auth/signup", data),

  login: (data: { email: string; password: string }) =>
    api.post("/auth/login", data),
};

// ─── News ─────────────────────────────────────────────────────────────────────

export const newsAPI = {
  getFeed: (limit = 20, skip = 0) =>
    api.get(`/news/feed?limit=${limit}&skip=${skip}`),

  getTrending: (limit = 10) =>
    api.get(`/news/trending?limit=${limit}`),

  search: (q: string, limit = 20) =>
    api.get(`/news/search?q=${encodeURIComponent(q)}&limit=${limit}`),

  getByCategory: (category: string, limit = 20, refresh = false) =>
    api.get(`/news/category/${category}?limit=${limit}&refresh=${refresh}`),

  getArticle: (url: string) =>
    api.get(`/news/article?url=${encodeURIComponent(url)}`),

  refresh: () => api.post("/news/refresh"),
};

// ─── Chat ─────────────────────────────────────────────────────────────────────

export const chatAPI = {
  sendMessage: (message: string) =>
    api.post("/chat/", { message }),

  indexNews: () => api.post("/chat/index"),

  clearHistory: () => api.delete("/chat/history"),
};

// ─── Preferences ─────────────────────────────────────────────────────────────

export const preferencesAPI = {
  get: () => api.get("/preferences/"),

  update: (categories: string[]) =>
    api.put("/preferences/", { categories }),
};
