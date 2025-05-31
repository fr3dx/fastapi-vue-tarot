//import * as jwtDecode from "jwt-decode"; // Importing JWT decode utility
import { useAuthStore } from '@/services/authStore'; // Import Pinia store
import router from '@/router/router'; // Import Vue Router
import api from "@/services/api";
import { decodeToken } from "@/services/jwtUtils";

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
    const res = await api.post(`${API_URL}/google`, {
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
    const res = await api.post(`${API_URL}/refresh`, {
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
