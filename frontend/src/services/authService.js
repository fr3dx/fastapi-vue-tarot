import axios from "@/utils/axiosSetup"; // Use the configured Axios instance
import * as jwtDecode from "jwt-decode"; // Importing JWT decode utility

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
 * @param {string} currentRefreshToken - The current refresh token.
 * @returns {Promise<Object>} - Returns an object with new access_token and possibly a new refresh_token.
 * @throws Throws error if refresh request fails or no refresh token is available.
 */
export const refreshAccessToken = async (currentRefreshToken) => {
  if (!currentRefreshToken) {
    // No refresh token available — caller should handle logout or re-authentication
    throw new Error("No refresh token provided for refreshAccessToken");
  }

  try {
    const res = await axios.post(`${API_URL}/refresh`, {
      refresh_token: currentRefreshToken,
    });
    // Return full response data
    return res.data;
  } catch (error) {
    console.error("Token refresh API call failed:", error);
    // Caller (store or interceptor) should handle logout on failure
    throw error;
  }
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