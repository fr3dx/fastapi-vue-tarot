import axios from "axios";
import * as jwtDecode from "jwt-decode"; // Importing JWT decode utility
import { useAuthStore } from '@/services/authStore'; // Import Pinia store
import router from '@/router/router'; // Import Vue Router

// Base URL for authentication API endpoints
const API_URL = "http://localhost:8000/api/auth";

/**
 * Authenticate user via Google token with backend API
 * @param {string} idToken - JWT token received from Google OAuth
 * @param {string} lang - User's preferred language for backend responses
 * @returns {Promise<Object>} - Returns an object containing access token, refresh token, and token type
 * @throws Will throw an error if the authentication request fails
 */
export const loginWithGoogle = async (idToken, lang) => {
  // This function is called by the store's login action.
  // The store action will handle setting the tokens.
  try {
    const res = await axios.post(`${API_URL}/google`, {
      token: idToken,
      lang: lang,
    });
    // Return the full response so the store can handle tokens and user data
    return res.data; 
  } catch (error) {
    console.error("Authentication API call failed:", error);
    throw error; // Propagate error for handling in the store action
  }
};

/**
 * Request a new access token using the refresh token from the Pinia store.
 * This function is called by the Axios interceptor or a store action.
 * @returns {Promise<Object>} - Returns an object containing the new access_token and potentially a new refresh_token.
 * @throws Will throw an error if the refresh request fails or no refresh token is available.
 */
export const refreshAccessToken = async () => {
  const authStore = useAuthStore();
  const currentRefreshToken = authStore.refreshToken;

  if (!currentRefreshToken) {
    // This should ideally be caught by the calling logic (e.g., interceptor)
    // and lead to logout.
    throw new Error("No refresh token available in store for refreshAccessToken");
  }

  try {
    const res = await axios.post(`${API_URL}/refresh`, {
      refresh_token: currentRefreshToken,
    });
    const { access_token, refresh_token: newRefreshToken } = res.data;
    // The caller (interceptor/store action) will use authStore.setTokens
    return { access_token, newRefreshToken };
  } catch (error) {
    console.error("Token refresh API call failed:", error);
    // The Pinia store action or interceptor that calls this will handle logout on failure.
    throw error;
  }
};

/**
 * Retrieve the stored access token from the Pinia store.
 * @returns {string|null} - JWT access token or null if not found.
 */
export const getAccessToken = () => {
  const authStore = useAuthStore();
  return authStore.accessToken;
};

/**
 * Decode a JWT token to extract payload data.
 * @param {string} token - JWT token string to decode.
 * @returns {Object|null} - Decoded token payload or null if decoding fails.
 */
export const decodeToken = (token) => {
  try {
    return jwtDecode.jwtDecode(token); // Using jwtDecode.jwtDecode as per original import
  } catch (error) {
    console.error("Failed to decode token:", error);
    return null;
  }
};

/**
 * Check if the access token (from Pinia store) is expired.
 * @returns {boolean} - True if token is expired or not present, false otherwise.
 */
export const isAccessTokenExpired = () => {
  const authStore = useAuthStore();
  const token = authStore.accessToken; // Get token from store
  if (!token) return true;

  const decoded = decodeToken(token);
  if (!decoded || !decoded.exp) return true;

  const currentTime = Math.floor(Date.now() / 1000);
  return decoded.exp < currentTime;
};

/**
 * Log out the current user by calling the Pinia store's logout action.
 * The store action will clear tokens and user state, and handle localStorage.
 */
export const logout = () => {
  const authStore = useAuthStore();
  authStore.logout();
  // Navigation to login page can be handled within the store's logout action
  // or by the component that calls this logout function.
  // For example: router.push('/login');
};

/**
 * Check whether the user is currently authenticated based on Pinia store state.
 * @returns {boolean} - True if user is authenticated, false otherwise.
 */
export const isAuthenticated = () => {
  const authStore = useAuthStore();
  return authStore.isAuthenticated; // Use the getter from the store
};

// --- Axios Interceptor Logic ---
let failedQueue = []; // Array to store failed requests during token refresh

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
    const authStore = useAuthStore(); // Call inside interceptor

    // Do not add token for auth endpoints like login/refresh or if it's a non-API call
    if (config.url.includes(`${API_URL}/google`) || config.url.includes(`${API_URL}/refresh`) || !config.url.startsWith(API_URL.substring(0, API_URL.lastIndexOf("/api")))) {
        return config;
    }

    const token = authStore.accessToken;

    if (token && isAccessTokenExpired()) {
      if (!authStore.isRefreshing) { // Check store's isRefreshing state
        authStore.setRefreshing(true);

        try {
          const { access_token: newAccessToken, newRefreshToken } = await refreshAccessToken();
          authStore.setTokens(newAccessToken, newRefreshToken); // Update store & localStorage via store action
          
          axios.defaults.headers.common.Authorization = `Bearer ${newAccessToken}`; // Update default header for subsequent requests
          config.headers.Authorization = `Bearer ${newAccessToken}`; // Update current request header
          
          processQueue(null, newAccessToken);
          return config;
        } catch (err) {
          console.error("Interceptor: Token refresh failed", err);
          authStore.logout(); // Logout on refresh failure (clears tokens, user, localStorage)
          router.push('/login'); // Redirect to login
          processQueue(err, null);
          return Promise.reject(err);
        } finally {
          authStore.setRefreshing(false);
        }
      } else {
        // Token is refreshing, queue the request
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
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

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

export default axios; // Export the configured axios instance
