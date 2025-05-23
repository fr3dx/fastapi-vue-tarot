import axios from 'axios';
import * as jwtDecode from 'jwt-decode'; // Importing JWT decode utility

// Base URL for authentication API endpoints
const API_URL = 'http://localhost:8000/api/auth';

/**
 * Authenticate user via Google token with backend API
 * @param {string} idToken - JWT token received from Google OAuth
 * @param {string} lang - User's preferred language for backend responses
 * @returns {Promise<Object>} - Returns an object containing access token, token type, and username
 * @throws Will throw an error if the authentication request fails
 */
export const loginWithGoogle = async (idToken, lang) => {
  try {
    const res = await axios.post(`${API_URL}/google`, {
      token: idToken,
      lang: lang,
    });
    const { access_token, token_type } = res.data; // Destructure response data, refresh_token removed

    // Persist access token locally
    localStorage.setItem('access_token', access_token);
    // refresh_token is no longer stored in localStorage

    // Optionally, you may want to save token_type or username as well for global usage
    // The 'username' field was mentioned in the return type but not destructured or returned previously.
    // Assuming it's not part of the TokenOut model from backend for now.
    return { access_token, token_type }; // Return authentication data, refresh_token removed
  } catch (error) {
    console.error("Authentication failed:", error);
    throw error; // Propagate error for handling in caller
  }
};

/**
 * Retrieve the stored access token from localStorage
 * @returns {string|null} - JWT access token or null if not found
 */
export const getAccessToken = () => { // Renamed from getTokens
  return localStorage.getItem('access_token');
  // Logic for refresh_token removed
};

/**
 * Check whether the user is currently authenticated.
 * This check is based on the presence of an access token.
 * @returns {boolean} - True if access token exists, false otherwise
 */
export const isAuthenticated = () => {
  const accessToken = getAccessToken(); // Uses the renamed function
  // Check for refresh_token removed
  return !!accessToken;
};

/**
 * Log out the current user.
 * This involves removing the local access token and calling the backend logout endpoint.
 */
export const logout = async () => { // Made async
  const token = getAccessToken(); // Get token for Authorization header

  try {
    if (token) {
      await axios.post(`${API_URL}/logout`, {}, { // Empty body for logout
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
    }
  } catch (error) {
    // Log error but proceed with local logout anyway
    console.error("Backend logout failed:", error.response ? error.response.data : error.message);
  } finally {
    // Always remove local token and perform client-side cleanup
    localStorage.removeItem('access_token');
    // localStorage.removeItem('refresh_token'); // Already removed as per previous step logic
    
    // TODO: Clear other local storage items if needed (e.g., user profile)
    // TODO: Consider redirecting the user to the login page or updating UI state globally.
    console.log("User logged out, local access token cleared.");
    // For example, to redirect:
    // window.location.href = '/login'; // Or use router if within a SPA framework
  }
};

// The refreshToken function is removed as its logic will be handled by the Axios interceptor.

/**
 * Decode a JWT token to extract payload data
 * @param {string} token - JWT token string to decode
 * @returns {Object|null} - Decoded token payload or null if decoding fails
 */
export const decodeToken = (token) => {
  try {
    // jwtDecode library exports a default function to decode tokens
    return jwtDecode.jwtDecode(token); // Or simply jwtDecode(token) depending on import
  } catch (error) {
    console.error("Failed to decode token:", error);
    return null; // Return null if token is invalid or decoding fails
  }
};

// --- Axios Interceptor for Token Refresh ---

let isRefreshing = false;
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

axios.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;

    // Check if the error is a 401, not a retry attempt, and not for the refresh token endpoint itself
    if (error.response && error.response.status === 401 && !originalRequest._retry && originalRequest.url !== `${API_URL}/refresh`) {
      if (isRefreshing) {
        // If token is already being refreshed, queue the request
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then(token => {
          originalRequest.headers['Authorization'] = 'Bearer ' + token;
          return axios(originalRequest); // Retry with new token
        }).catch(err => {
          return Promise.reject(err); // Propagate error if queue processing fails
        });
      }

      originalRequest._retry = true; // Mark that this request has been retried
      isRefreshing = true;

      try {
        // Attempt to refresh the token using the HTTP-only cookie
        const refreshResponse = await axios.post(`${API_URL}/refresh`, {}, { withCredentials: true });
        
        const newAccessToken = refreshResponse.data.access_token;
        if (!newAccessToken) {
          throw new Error("New access token not found in refresh response.");
        }

        localStorage.setItem('access_token', newAccessToken);
        
        // Optional: Update default Axios header if your app uses it globally
        // axios.defaults.headers.common['Authorization'] = 'Bearer ' + newAccessToken;

        // Update the header of the original request
        originalRequest.headers['Authorization'] = 'Bearer ' + newAccessToken;
        
        // Process the queue of failed requests with the new token
        processQueue(null, newAccessToken);
        
        // Retry the original request with the new token
        return axios(originalRequest);

      } catch (refreshError) {
        // If refresh fails, process queue with error, logout user, and reject
        processQueue(refreshError, null);
        console.error("Refresh token failed, logging out:", refreshError.response ? refreshError.response.data : refreshError.message);
        await logout(); // Call the updated logout function (ensure it's async and handles errors)
        
        // Optional: Redirect to login page
        // window.location.href = '/login'; // Or use router navigation

        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false; // Reset refreshing state
      }
    }

    // For errors not related to 401 or other conditions, just propagate them
    return Promise.reject(error);
  }
);
