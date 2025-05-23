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
    const { access_token, refresh_token, token_type, username } = res.data; // Destructure response data

    // Persist access token and refresh token locally
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);
    // Optionally, you may want to save token_type or username as well for global usage

    return { access_token, refresh_token, token_type, username }; // Return useful authentication data
  } catch (error) {
    console.error("Authentication failed:", error);
    throw error; // Propagate error for handling in caller
  }
};

/**
 * Retrieve the stored access and refresh tokens from localStorage
 * @returns {{accessToken: string|null, refreshToken: string|null}} - Object containing JWT tokens or null if not found
 */
export const getTokens = () => {
  const accessToken = localStorage.getItem('access_token');
  const refreshToken = localStorage.getItem('refresh_token');
  return { accessToken, refreshToken };
};

/**
 * Check whether the user is currently authenticated.
 * This check is based on the presence of both access and refresh tokens.
 * Optional: Could add access token expiration check here and attempt refresh.
 * @returns {boolean} - True if both tokens exist, false otherwise
 */
export const isAuthenticated = () => {
  const { accessToken, refreshToken } = getTokens();
  // For now, just checking for presence. Expiration check can be added.
  // Example of expiration check (and proactive refresh):
  // if (accessToken) {
  //   const decoded = decodeToken(accessToken);
  //   if (decoded && decoded.exp * 1000 < Date.now()) {
  //     // Token expired, try to refresh it or return false
  //     // console.log("Access token expired, attempting refresh or flagging as not authenticated.");
  //     // For simplicity here, we'll rely on API calls to trigger refresh if needed.
  //     // Or, you could attempt refreshToken() here.
  //     return false; // Or attempt refresh and return based on its success
  //   }
  // }
  return !!accessToken && !!refreshToken;
};

/**
 * Log out the current user by removing authentication tokens.
 */
export const logout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  // TODO: Clear other local storage items if needed (e.g., user profile)
  // Consider redirecting the user to the login page or updating UI state.
  console.log("User logged out, tokens cleared.");
};

/**
 * Attempt to refresh the access token using the stored refresh token.
 * @returns {Promise<string>} - The new access token.
 * @throws Will throw an error if refresh token is not found, or if API refresh fails.
 */
export const refreshToken = async () => {
  const { refreshToken: currentRefreshToken } = getTokens();

  if (!currentRefreshToken) {
    console.error("No refresh token available for refreshing session.");
    logout(); // Ensure user is logged out if refresh token is missing
    throw new Error("Refresh token not found. User logged out.");
  }

  try {
    const res = await axios.post(`${API_URL}/refresh`, {
      refresh_token: currentRefreshToken,
    });
    const { access_token: newAccessToken } = res.data;

    if (!newAccessToken) {
      throw new Error("New access token not found in refresh response.");
    }

    localStorage.setItem('access_token', newAccessToken);
    console.log("Access token refreshed successfully.");
    return newAccessToken;
  } catch (error) {
    console.error("Failed to refresh token:", error.response ? error.response.data : error.message);
    logout(); // Critical failure, log out the user
    // Propagate the error for the caller to handle (e.g., redirect to login)
    throw new Error(error.response?.data?.detail || "Session expired. Please log in again.");
  }
};

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
