import axios from "axios";
import * as jwtDecode from "jwt-decode"; // Importing JWT decode utility

// Base URL for authentication API endpoints
const API_URL = "http://localhost:8000/api/auth";

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
    const { access_token, refresh_token, token_type } = res.data; // Destructure response data

    // Persist access token locally for future authenticated requests
    localStorage.setItem("access_token", access_token);
    localStorage.setItem("refresh_token", refresh_token);
    // Optionally, you may want to save token_type or username as well for global usage

    return { access_token, refresh_token, token_type }; // Return useful authentication data
  } catch (error) {
    console.error("Authentication failed:", error);
    throw error; // Propagate error for handling in caller
  }
};

export const refreshAccessToken = async () => {
  const refreshToken = localStorage.getItem("refresh_token");
  if (!refreshToken) {
    throw new Error("No refresh token available");
  }

  try {
    const res = await axios.post(`${API_URL}/refresh`, {
      refresh_token: refreshToken,
    });

    const { access_token, refresh_token: newRefreshToken } = res.data;

    // Frissítjük a tárolt tokeneket (rotálás támogatása)
    localStorage.setItem("access_token", access_token);
    if (newRefreshToken) {
      localStorage.setItem("refresh_token", newRefreshToken);
    }

    return access_token;
  } catch (error) {
    console.error("Token refresh failed:", error);
    logout(); // Token hibánál tisztítás
    throw error;
  }
};

/**
 * Retrieve the stored access token from localStorage
 * @returns {string|null} - JWT access token or null if not found
 */
export const getAccessToken = () => {
  return localStorage.getItem("access_token");
};

/**
 * Check whether the user is currently authenticated
 * This is a simple check based on the presence of a token.
 * Further validation like token expiration can be added here.
 * @returns {boolean} - True if access token exists, false otherwise
 */
export const isAuthenticated = () => {
  const token = getAccessToken();
  // TODO: Add token expiration verification if token includes exp claim
  return !!token;
};

/**
 * Log out the current user by removing authentication tokens
 * Also consider clearing any other locally stored user data here
 */
export const logout = () => {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  // TODO: Clear other local storage items if needed (e.g., user profile, refresh tokens)
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

// Validate Access token
export const isAccessTokenExpired = () => {
  const token = getAccessToken();
  if (!token) return true;

  const decoded = decodeToken(token);
  if (!decoded || !decoded.exp) return true;

  const currentTime = Math.floor(Date.now() / 1000);
  return decoded.exp < currentTime;
};

// Token frissítés interceptor
axios.interceptors.request.use(
  async (config) => {
    if (isAccessTokenExpired()) {
      try {
        const newAccessToken = await refreshAccessToken();
        config.headers.Authorization = `Bearer ${newAccessToken}`;
      } catch (err) {
        console.warn("Failed to refresh token. User may be logged out.");
      }
    } else {
      const token = getAccessToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);
