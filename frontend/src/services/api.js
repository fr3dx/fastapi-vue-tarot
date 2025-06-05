import axios from "axios";
import router from '@/router/router';
import { useAuthStore } from '@/services/authStore';
import { isAccessTokenExpired, refreshAccessToken } from '@/services/authService';
import { handleApiError } from './errorHandler';

const API_URL = import.meta.env.VITE_APP_API_URL;

// Create an Axios instance with the base URL from environment variables
const api = axios.create({
  baseURL: API_URL,
});

// Queue to hold failed requests while access token is being refreshed
let failedQueue = [];

// Flag to indicate if token refresh is currently in progress
let isRefreshing = false;

/**
 * Process the queue of failed requests.
 * Resolves all queued promises with the new token if successful,
 * or rejects them with the error if token refresh failed.
 * @param {Error|null} error - Error object if refresh failed, otherwise null
 * @param {string|null} token - New access token if refresh succeeded, otherwise null
 */
const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) prom.reject(error);
    else prom.resolve(token);
  });
  failedQueue = [];
};

// Request interceptor to add authorization header and handle token refresh logic
api.interceptors.request.use(
  async (config) => {
    const authStore = useAuthStore();
    const token = authStore.accessToken;

    // Skip attaching token to authentication-related endpoints
    if (
      config.url.includes("/google") ||    // OAuth login endpoints
      config.url.includes("/refresh")      // Token refresh endpoint
    ) {
      return config;
    }

    // If token exists and is expired, attempt to refresh it
    if (token && isAccessTokenExpired()) {
      // If no refresh in progress, start refresh process
      if (!isRefreshing) {
        isRefreshing = true;
        try {
          // Call refresh token API to get new tokens
          const { access_token: newToken, newRefreshToken } = await refreshAccessToken();

          // Update tokens in auth store
          authStore.setTokens(newToken, newRefreshToken);

          // Update the current request's Authorization header with new token
          config.headers.Authorization = `Bearer ${newToken}`;

          // Resolve all queued requests with new token
          processQueue(null, newToken);
        } catch (err) {
          // If refresh fails, log out user and redirect to login
          authStore.logout();
          router.push("/login");

          // Reject all queued requests with error
          processQueue(err, null);

          // Propagate error to current request
          throw err;
        } finally {
          // Reset refreshing flag regardless of success or failure
          isRefreshing = false;
        }
      } else {
        // If refresh is already in progress, queue this request until it completes
        return new Promise((resolve, reject) => {
          failedQueue.push({
            resolve: (token) => {
              // Once token refresh completes successfully, retry the request with new token
              config.headers.Authorization = `Bearer ${token}`;
              resolve(config);
            },
            reject: (err) => reject(err),
          });
        });
      }
    } else if (token) {
      // If token exists and is valid, attach it to the Authorization header
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  // Pass through any request errors
  (error) => Promise.reject(error)
);

// Response interceptor - currently passes responses/errors through without modification
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    return Promise.reject(error);
  }
);

export default api;
