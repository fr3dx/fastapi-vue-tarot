import axios from 'axios';
import { useAuthStore } from '@/services/authStore';
import router from '@/router/router';

const API_URL = import.meta.env.VITE_APP_API_URL;

let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

axios.interceptors.request.use(
  async (config) => {
    const authStore = useAuthStore();

    // Skip adding token to authentication endpoints and non-API calls
    if (
      config.url.includes(`${API_URL}/google`) ||
      config.url.includes(`${API_URL}/refresh`) ||
      (API_URL && !config.url.startsWith(API_URL.substring(0, API_URL.lastIndexOf("/api"))))
    ) {
      return config;
    }

    const token = authStore.accessToken;

    // Check if token exists and if it's expired (using isAuthenticated getter)
    if (token && !authStore.isAuthenticated) {
      if (!authStore.isRefreshing) {
        authStore.setRefreshing(true);
        console.log("Request Interceptor: Proactively refreshing token");
        try {
          const newAccessToken = await authStore.handleTokenRefresh();
          axios.defaults.headers.common.Authorization = `Bearer ${newAccessToken}`;
          config.headers.Authorization = `Bearer ${newAccessToken}`;
          processQueue(null, newAccessToken);
          console.log("Request Interceptor: Token refreshed proactively, re-dispatching original request");
          // Return axios(config) to re-dispatch the original request with the new token.
          // However, if the original request config was already modified, just returning config might be fine
          // if the modifications are picked up by the ongoing request processing.
          // Forcing a re-dispatch with axios(config) is more robust.
          return axios(config); 
        } catch (err) {
          processQueue(err, null);
          // authStore.logout(); // Already handled by handleTokenRefresh
          // router.push('/login'); // Potentially handled by handleTokenRefresh or global navigation guards
          console.error("Request Interceptor: Proactive refresh failed", err);
          return Promise.reject(err);
        } finally {
          authStore.setRefreshing(false);
        }
      } else {
        console.log("Request Interceptor: Token refresh in progress, queueing request");
        return new Promise((resolve, reject) => {
          failedQueue.push({
            resolve: (newAccessToken) => {
              config.headers.Authorization = `Bearer ${newAccessToken}`;
              resolve(config);
            },
            reject: (err) => {
              reject(err);
            },
          });
        });
      }
    } else if (token) {
      // Token exists and is not expired
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

axios.interceptors.response.use(
  response => response,
  async (error) => {
    const originalRequest = error.config;
    const authStore = useAuthStore();

    // Check if it's a 401 error, not from a refresh token request, and we haven't tried to refresh yet for this request
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true; // Mark that we've tried to refresh for this request
      console.log("Response Interceptor: Caught 401, attempting refresh");

      // If the failed request was the refresh token request itself, logout and redirect
      if (originalRequest.url.includes(`${API_URL}/refresh`)) {
        console.error("Response Interceptor: Refresh token request itself failed. Logging out.");
        authStore.logout(); // Ensure user is logged out
        router.push('/login'); // Redirect to login
        return Promise.reject(error); // Reject with the original error
      }

      if (!authStore.isRefreshing) {
        authStore.setRefreshing(true);
        try {
          const newAccessToken = await authStore.handleTokenRefresh(); // This should fetch and set the new token
          axios.defaults.headers.common['Authorization'] = `Bearer ${newAccessToken}`;
          originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
          processQueue(null, newAccessToken); // Process any queued requests
          console.log("Response Interceptor: Token refreshed, retrying original request", originalRequest.url);
          return axios(originalRequest); // Retry original request
        } catch (refreshError) {
          console.error("Response Interceptor: Token refresh failed", refreshError);
          processQueue(refreshError, null);
          // authStore.logout(); // This is likely handled within handleTokenRefresh on error
          // router.push('/login'); // Also potentially handled by handleTokenRefresh or global guards
          return Promise.reject(refreshError);
        } finally {
          authStore.setRefreshing(false);
        }
      } else {
        // Token is refreshing, queue the request
        console.log("Response Interceptor: Token refresh in progress, queueing original request", originalRequest.url);
        return new Promise((resolve, reject) => {
          failedQueue.push({
            resolve: (token) => {
              originalRequest.headers['Authorization'] = `Bearer ${token}`;
              console.log("Response Interceptor: Retrying queued request with new token", originalRequest.url);
              resolve(axios(originalRequest));
            },
            reject: (err) => {
              console.error("Response Interceptor: Queued request failed after refresh attempt", err);
              reject(err);
            }
          });
        });
      }
    }
    return Promise.reject(error);
  }
);

export default axios;
