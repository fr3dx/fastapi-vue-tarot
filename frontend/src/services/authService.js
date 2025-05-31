import axios from "axios";
import * as jwtDecode from "jwt-decode"; // Importing JWT decode utility
import { useAuthStore } from '@/services/authStore'; // Import Pinia store
import router from '@/router/router'; // Import Vue Router

// Base URL for authentication API endpoints, loaded from environment variables
const API_URL = import.meta.env.VITE_APP_API_URL;

/**
 * Authenticate user via Google OAuth token with backend API.
 * @param {string} idToken - JWT token received from Google OAuth
 * @param {string} lang - User's preferred language for backend responses
 * @returns {Promise<Object>} - Returns an object containing access token, refresh token, and token type
 * @throws Throws an error if the authentication request fails
 */
export const loginWithGoogle = async (idToken, lang) => {
  // This function is called by the store's login action.
  // The store handles setting tokens upon successful response.
  try {
    const res = await axios.post(`${API_URL}/google`, {
      token: idToken,
      lang: lang,
    });
    // Return full response data for further processing in the store
    return res.data; 
  } catch (error) {
    console.error("Authentication API call failed:", error);
    throw error; // Propagate error to be handled in the store action
  }
};

/**
 * Request a new access token using the stored refresh token.
 * Typically called by Axios interceptor or store action when token is expired.
 * @returns {Promise<Object>} - Returns an object with new access_token and possibly a new refresh_token.
 * @throws Throws error if refresh request fails or no refresh token is available.
 */
export const refreshAccessToken = async () => {
  const authStore = useAuthStore();
  const currentRefreshToken = authStore.refreshToken;

  if (!currentRefreshToken) {
    // No refresh token available — caller should handle logout or re-authentication
    throw new Error("No refresh token available in store for refreshAccessToken");
  }

  try {
    const res = await axios.post(`${API_URL}/refresh`, {
      refresh_token: currentRefreshToken,
    });
    const { access_token, refresh_token: newRefreshToken } = res.data;
    // Caller will update tokens in the store
    return { access_token, newRefreshToken };
  } catch (error) {
    console.error("Token refresh API call failed:", error);
    // Caller (store or interceptor) should handle logout on failure
    throw error;
  }
};

/**
 * Retrieve the current access token from the Pinia store.
 * @returns {string|null} - JWT access token or null if not available.
 */
export const getAccessToken = () => {
  const authStore = useAuthStore();
  return authStore.accessToken;
};

/**
 * Decode a JWT token to extract the payload.
 * @param {string} token - JWT token string to decode.
 * @returns {Object|null} - Decoded token payload or null if decoding fails.
 */
export const decodeToken = (token) => {
  try {
    return jwtDecode.jwtDecode(token); // Using jwtDecode.jwtDecode as per import style
  } catch (error) {
    console.error("Failed to decode token:", error);
    return null;
  }
};

/**
 * Check if the current access token stored in Pinia is expired.
 * @returns {boolean} - True if token is expired or not present, false otherwise.
 */
export const isAccessTokenExpired = () => {
  const authStore = useAuthStore();
  const token = authStore.accessToken;
  if (!token) return true;

  const decoded = decodeToken(token);
  if (!decoded || !decoded.exp) return true;

  const currentTime = Math.floor(Date.now() / 1000);
  return decoded.exp < currentTime;
};

/**
 * Log out the current user by calling the Pinia store's logout action.
 * The store action clears tokens and user state.
 */
export const logout = () => {
  const authStore = useAuthStore();
  authStore.logout();
  // Optional: navigate to login page after logout
  // router.push('/login');
};

/**
 * Check if the user is currently authenticated based on the Pinia store state.
 * @returns {boolean} - True if authenticated, false otherwise.
 */
export const isAuthenticated = () => {
  const authStore = useAuthStore();
  return authStore.isAuthenticated; // Access the getter from the store
};

// --- Axios Request Interceptor ---

// Queue to hold failed requests while token refresh is in progress
let failedQueue = [];

/**
 * Processes the queued requests after token refresh either succeeds or fails.
 * @param {Error|null} error - Error if token refresh failed
 * @param {string|null} token - New access token if refresh succeeded
 */
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
      !config.url.startsWith(API_URL.substring(0, API_URL.lastIndexOf("/api")))
    ) {
      return config;
    }

    const token = authStore.accessToken;

    // If token exists and is expired, attempt to refresh
    if (token && isAccessTokenExpired()) {
      if (!authStore.isRefreshing) {
        authStore.setRefreshing(true);

        try {
          const { access_token: newAccessToken, newRefreshToken } = await refreshAccessToken();
          authStore.setTokens(newAccessToken, newRefreshToken);

          // Update authorization headers for all subsequent requests
          axios.defaults.headers.common.Authorization = `Bearer ${newAccessToken}`;
          config.headers.Authorization = `Bearer ${newAccessToken}`;

          processQueue(null, newAccessToken);
          return config;
        } catch (err) {
          console.error("Interceptor: Token refresh failed", err);
          authStore.logout(); // Clear auth data on failure
          router.push('/login'); // Redirect to login page
          processQueue(err, null);
          return Promise.reject(err);
        } finally {
          authStore.setRefreshing(false);
        }
      } else {
        // Token refresh already in progress, queue this request
        return new Promise((resolve, reject) => {
          failedQueue.push({
            resolve: (newAccessToken) => {
              config.headers.Authorization = `Bearer ${newAccessToken}`;
              resolve(config);
            },
            reject: (err) => {
              reject(err);
            }
          });
        });
      }
    } else if (token) {
      // Token is valid, attach it to the request headers
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Optional response interceptor commented out for handling 401 errors and token refresh retries


// Optional: Response interceptor for handling 401s if request interceptor somehow misses an expired token.
// axios.interceptors.response.use(
//   response => response,
//   async error => {
//     const originalRequest = error.config;
//     const authStore = useAuthStore();
// 
//     // Check if it's a 401 error, not from a refresh token request, and we haven't tried to refresh yet for this request
//     if (error.response.status === 401 && !originalRequest._retry && originalRequest.url !== `${API_URL}/refresh`) {
//       originalRequest._retry = true; // Mark that we've tried to refresh for this request
// 
//       if (!authStore.isRefreshing) {
//         authStore.setRefreshing(true);
//         try {
//           const { access_token: newAccessToken, newRefreshToken } = await refreshAccessToken();
//           authStore.setTokens(newAccessToken, newRefreshToken);
//           axios.defaults.headers.common['Authorization'] = `Bearer ${newAccessToken}`;
//           originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
//           processQueue(null, newAccessToken); // Process any queued requests
//           return axios(originalRequest); // Retry original request
//         } catch (refreshError) {
//           console.error("Response Interceptor: Token refresh failed", refreshError);
//           authStore.logout();
//           router.push('/login');
//           processQueue(refreshError, null);
//           return Promise.reject(refreshError);
//         } finally {
//           authStore.setRefreshing(false);
//         }
//       } else {
//         // Token is refreshing, queue the request
//         return new Promise((resolve, reject) => {
//           failedQueue.push({
//             resolve: (newAccessToken) => {
//               originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
//               resolve(axios(originalRequest));
//             },
//             reject: (err) => {
//               reject(err);
//             }
//           });
//         });
//       }
//     }
//     return Promise.reject(error);
//   }
// );

// export default the axios instance to be used throughout the app
export default axios;