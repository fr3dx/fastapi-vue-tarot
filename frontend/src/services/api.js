import axios from "axios";
import router from '@/router/router';
import { useAuthStore } from '@/services/authStore';
import { isAccessTokenExpired, refreshAccessToken } from '@/services/authService';
const API_URL = import.meta.env.VITE_APP_API_URL;

const api = axios.create({
  baseURL: API_URL,
});

// Failed request queue
let failedQueue = [];
let isRefreshing = false;

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) prom.reject(error);
    else prom.resolve(token);
  });
  failedQueue = [];
};

api.interceptors.request.use(
  async (config) => {
    const authStore = useAuthStore();
    const token = authStore.accessToken;

    // Skip adding token for auth endpoints
    if (
      config.url.includes("/google") ||
      config.url.includes("/refresh")
    ) {
      return config;
    }

    if (token && isAccessTokenExpired()) {
      if (!isRefreshing) {
        isRefreshing = true;
        try {
          const { access_token: newToken, newRefreshToken } = await refreshAccessToken();
          authStore.setTokens(newToken, newRefreshToken);
          config.headers.Authorization = `Bearer ${newToken}`;
          processQueue(null, newToken);
        } catch (err) {
          authStore.logout();
          router.push("/login");
          processQueue(err, null);
          throw err;
        } finally {
          isRefreshing = false;
        }
      } else {
        return new Promise((resolve, reject) => {
          failedQueue.push({
            resolve: (token) => {
              config.headers.Authorization = `Bearer ${token}`;
              resolve(config);
            },
            reject: (err) => reject(err),
          });
        });
      }
    } else if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

export default api;
