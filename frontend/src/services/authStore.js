import { defineStore } from 'pinia';
import { loginWithGoogle, decodeToken } from '@/services/authService';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    // JWT access token for API authentication, loaded from localStorage if present
    accessToken: localStorage.getItem('access_token') || null,
    // JWT refresh token for renewing the access token, loaded from localStorage if present
    refreshToken: localStorage.getItem('refresh_token') || null,
    // User information decoded from the access token; null if not logged in
    user: null,
    // Loading state to indicate ongoing authentication-related operations
    isLoading: false,
    // Lock flag to prevent concurrent token refresh operations
    isRefreshing: false,
  }),

  getters: {
    /**
     * Checks whether the user is currently authenticated.
     * Validates the access token expiry timestamp.
     * Returns true if access token exists and is not expired.
     */
    isAuthenticated: (state) => {
      if (!state.accessToken) return false;
      try {
        const decoded = decodeToken(state.accessToken);
        const now = Math.floor(Date.now() / 1000);
        return decoded.exp && decoded.exp > now;
      } catch (error) {
        console.error('Invalid access token in isAuthenticated:', error);
        return false;
      }
    },

    /**
     * Returns the decoded access token payload if available.
     * Returns null if no valid access token exists or decoding fails.
     */
    decodedAccessToken: (state) => {
      if (state.accessToken) {
        try {
          return decodeToken(state.accessToken);
        } catch (error) {
          console.error('Error decoding access token:', error);
          return null;
        }
      }
      return null;
    },
  },

  actions: {
    /**
     * Performs user login using Google OAuth token and preferred language.
     * Sets loading state during login process.
     * Stores access and refresh tokens on successful login.
     * Throws error to caller if login fails.
     */
    async login(googleIdToken, language) {
      this.setLoading(true);
      try {
        const response = await loginWithGoogle(googleIdToken, language);
        if (response && response.access_token && response.refresh_token) {
          this.setTokens(response.access_token, response.refresh_token);
        }
        return response; 
      } catch (error) {
        console.error('Login failed:', error);
        this.clearAuthData(); // Clear authentication data if login fails
        throw error;
      } finally {
        this.setLoading(false);
      }
    },

    /**
     * Logs out the user by clearing all authentication data.
     * Navigation to login page should be handled by the component or router.
     */
    logout() {
      this.clearAuthData();
    },

    /**
     * Sets new access and refresh tokens in state and localStorage.
     * Decodes the user information from the new access token.
     */
    setTokens(newAccessToken, newRefreshToken) {
      this.accessToken = newAccessToken;
      this.refreshToken = newRefreshToken;
      localStorage.setItem('access_token', newAccessToken);
      localStorage.setItem('refresh_token', newRefreshToken);

      if (newAccessToken) {
        try {
          this.user = decodeToken(newAccessToken);
        } catch (error) {
          console.error('Error decoding token on setTokens:', error);
          this.user = null;
        }
      } else {
        this.user = null;
      }
    },

    /**
     * Clears authentication tokens and user data from state and localStorage.
     */
    clearAuthData() {
      this.accessToken = null;
      this.refreshToken = null;
      this.user = null;
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    },

    /**
     * Sets the token refresh lock status to prevent concurrent refreshes.
     */
    setRefreshing(status) {
      this.isRefreshing = status;
    },

    /**
     * Sets the loading status for authentication-related processes.
     */
    setLoading(status) {
      this.isLoading = status;
    },

    /**
     * Initializes the user state from the stored access token if present.
     * Decodes the token and populates user data.
     * Clears auth data if token is invalid.
     * Intended to be called once when the store initializes.
     */
    initializeUser() {
      if (this.accessToken) {
        try {
          this.user = decodeToken(this.accessToken);
        } catch (error) {
          console.error('Error decoding token on initializeUser:', error);
          this.user = null;
          this.clearAuthData(); 
        }
      }
    }
  },
});