import { defineStore } from 'pinia';
import { loginWithGoogle, decodeToken } from '@/services/authService';

/**
 * Authentication configuration constants
 * Centralized configuration for localStorage keys and other auth-related settings
 */
const AUTH_CONFIG = {
  ACCESS_TOKEN_KEY: 'access_token',
  REFRESH_TOKEN_KEY: 'refresh_token',
};

/**
 * Authentication error type definitions
 * Standardized error types for consistent error handling across the application
 */
const AUTH_ERRORS = {
  LOGIN_FAILED: 'LOGIN_FAILED',
  TOKEN_DECODE_FAILED: 'TOKEN_DECODE_FAILED',
  TOKEN_EXPIRED: 'TOKEN_EXPIRED',
};

/**
 * Safe localStorage wrapper for SSR compatibility
 * Provides error handling and server-side rendering compatibility
 * Prevents crashes when localStorage is not available (e.g., in Node.js environment)
 */
const safeLocalStorage = {
  /**
   * Safely retrieves an item from localStorage
   * @param {string} key - The localStorage key to retrieve
   * @returns {string|null} The stored value or null if not found/error occurred
   */
  getItem: (key) => {
    if (typeof window === 'undefined') return null;
    try {
      return localStorage.getItem(key);
    } catch (error) {
      console.warn(`Failed to read from localStorage: ${key}`, error);
      return null;
    }
  },

  /**
   * Safely stores an item in localStorage
   * @param {string} key - The localStorage key
   * @param {string} value - The value to store
   */
  setItem: (key, value) => {
    if (typeof window === 'undefined') return;
    try {
      localStorage.setItem(key, value);
    } catch (error) {
      console.warn(`Failed to write to localStorage: ${key}`, error);
    }
  },

  /**
   * Safely removes an item from localStorage
   * @param {string} key - The localStorage key to remove
   */
  removeItem: (key) => {
    if (typeof window === 'undefined') return;
    try {
      localStorage.removeItem(key);
    } catch (error) {
      console.warn(`Failed to remove from localStorage: ${key}`, error);
    }
  }
};

/**
 * Creates a standardized authentication error object
 * @param {string} type - Error type from AUTH_ERRORS
 * @param {string} message - Human-readable error message
 * @param {Error|null} originalError - Original error object for debugging
 * @returns {Object} Structured error object with metadata
 */
const createAuthError = (type, message, originalError = null) => ({
  type,
  message,
  originalError,
  timestamp: new Date().toISOString(),
});

/**
 * Pinia store for authentication state management
 * Handles user authentication, token management, and auth-related UI states
 */
export const useAuthStore = defineStore('auth', {
  state: () => ({
    /** JWT access token for API authentication - retrieved from localStorage on init */
    accessToken: safeLocalStorage.getItem(AUTH_CONFIG.ACCESS_TOKEN_KEY) || null,
    
    /** JWT refresh token for renewing the access token - retrieved from localStorage on init */
    refreshToken: safeLocalStorage.getItem(AUTH_CONFIG.REFRESH_TOKEN_KEY) || null,
    
    /** User information decoded from the access token */
    user: null,
    
    /** Loading state indicator for authentication operations (login, token refresh, etc.) */
    isLoading: false,
    
    /** Lock flag to prevent concurrent token refresh operations */
    isRefreshing: false,
    
    /** Last authentication error that occurred - used for error display in UI */
    lastError: null,
  }),

  getters: {
    /**
     * Determines if the user is currently authenticated
     * Validates the access token's existence and expiry timestamp
     * @param {Object} state - Pinia state object
     * @returns {boolean} True if user has valid, non-expired access token
     */
    isAuthenticated: (state) => {
      if (!state.accessToken) return false;
      
      try {
        const decoded = decodeToken(state.accessToken);
        if (!decoded || !decoded.exp) return false;
        
        // Check if token is expired (exp is in seconds, Date.now() is in milliseconds)
        const now = Math.floor(Date.now() / 1000);
        const isValid = decoded.exp > now;
        
        if (!isValid) {
          // Token expired - log warning but don't clear data here to avoid side effects in getter
          console.warn('Access token has expired');
        }
        
        return isValid;
      } catch (error) {
        console.error('Invalid access token in isAuthenticated:', error);
        return false;
      }
    },

    /**
     * Returns the decoded access token payload if available
     * @param {Object} state - Pinia state object
     * @returns {Object|null} Decoded JWT payload or null if token invalid/missing
     */
    decodedAccessToken: (state) => {
      if (!state.accessToken) return null;
      
      try {
        return decodeToken(state.accessToken);
      } catch (error) {
        console.error('Error decoding access token:', error);
        return null;
      }
    },

    /**
     * Indicates if any authentication operation is in progress
     * Useful for showing loading states in UI components
     * @param {Object} state - Pinia state object
     * @returns {boolean} True if login or token refresh is in progress
     */
    isBusy: (state) => state.isLoading || state.isRefreshing,

    /**
     * Returns user's display name for UI purposes
     * Falls back to email if name not available, then to generic string
     * @param {Object} state - Pinia state object
     * @returns {string|null} User display name or null if no user data
     */
    userDisplayName: (state) => {
      if (!state.user) return null;
      return state.user.name || state.user.email || 'Unknown User';
    },
  },

  actions: {
    /**
     * Authenticates user using Google OAuth ID token
     * Handles the complete login flow including token storage and user data extraction
     * @param {string} googleIdToken - Google OAuth ID token from client-side authentication
     * @param {string} language - User's preferred language (default: 'en')
     * @returns {Promise<Object>} Authentication response from server
     * @throws {Object} Structured authentication error
     */
    async login(googleIdToken, language = 'en') {
      // Validate required parameters
      if (!googleIdToken) {
        const error = createAuthError(
          AUTH_ERRORS.LOGIN_FAILED,
          'Google ID token is required'
        );
        this.lastError = error;
        throw error;
      }

      this.setLoading(true);
      this.lastError = null;

      try {
        // Call authentication service
        const response = await loginWithGoogle(googleIdToken, language);
        
        // Validate server response contains required tokens
        if (!response?.access_token || !response?.refresh_token) {
          throw createAuthError(
            AUTH_ERRORS.LOGIN_FAILED,
            'Invalid response from authentication server'
          );
        }

        // Store tokens and decode user information
        this.setTokens(response.access_token, response.refresh_token);
        
        console.info('User successfully logged in');
        return response;
      } catch (error) {
        // Standardize error format - preserve structured errors, wrap others
        const authError = error.type ? error : createAuthError(
          AUTH_ERRORS.LOGIN_FAILED,
          error.response?.data?.message || error.message || 'Login failed',
          error
        );
        
        this.lastError = authError;
        this.clearAuthData(); // Clean up on login failure
        
        console.error('Login failed:', authError);
        throw authError;
      } finally {
        this.setLoading(false);
      }
    },

    /**
     * Logs out the current user
     * Clears all authentication data from state and localStorage
     */
    logout() {
      console.info('User logged out');
      this.clearAuthData();
      this.lastError = null;
    },

    /**
     * Updates authentication tokens in both state and localStorage
     * Automatically decodes and sets user information from the new access token
     * @param {string} newAccessToken - New JWT access token
     * @param {string} newRefreshToken - New JWT refresh token
     */
    setTokens(newAccessToken, newRefreshToken) {
      if (!newAccessToken || !newRefreshToken) {
        console.warn('Attempted to set invalid tokens');
        return;
      }

      // Update Pinia state
      this.accessToken = newAccessToken;
      this.refreshToken = newRefreshToken;
      
      // Persist to localStorage for session continuity
      safeLocalStorage.setItem(AUTH_CONFIG.ACCESS_TOKEN_KEY, newAccessToken);
      safeLocalStorage.setItem(AUTH_CONFIG.REFRESH_TOKEN_KEY, newRefreshToken);

      // Extract and set user information from access token
      this.decodeAndSetUser(newAccessToken);
    },

    /**
     * Decodes JWT access token and extracts user information
     * Sets the user state with essential user data only
     * @param {string} accessToken - JWT access token to decode
     */
    decodeAndSetUser(accessToken) {
      if (!accessToken) {
        this.user = null;
        return;
      }

      try {
        const decodedUser = decodeToken(accessToken);
        if (decodedUser) {
          // Store only essential user data to minimize state size
          this.user = {
            id: decodedUser.sub || decodedUser.id,           // User ID from 'sub' claim or fallback
            email: decodedUser.email,                         // User email address
            name: decodedUser.name,                          // User display name
            picture: decodedUser.picture,                    // User profile picture URL
            exp: decodedUser.exp,                            // Token expiration timestamp
            iat: decodedUser.iat,                            // Token issued at timestamp
          };
        } else {
          this.user = null;
        }
      } catch (error) {
        const authError = createAuthError(
          AUTH_ERRORS.TOKEN_DECODE_FAILED,
          'Failed to decode user information from token',
          error
        );
        
        this.lastError = authError;
        this.user = null;
        console.error('Error decoding token:', authError);
      }
    },

    /**
     * Completely clears all authentication data
     * Removes tokens and user data from both Pinia state and localStorage
     * Resets all authentication-related flags
     */
    clearAuthData() {
      // Clear Pinia state
      this.accessToken = null;
      this.refreshToken = null;
      this.user = null;
      this.isRefreshing = false;
      
      // Clear localStorage persistence
      safeLocalStorage.removeItem(AUTH_CONFIG.ACCESS_TOKEN_KEY);
      safeLocalStorage.removeItem(AUTH_CONFIG.REFRESH_TOKEN_KEY);
    },

    /**
     * Sets the token refresh operation lock status
     * Prevents concurrent refresh operations that could cause race conditions
     * @param {boolean} status - True to lock, false to unlock
     */
    setRefreshing(status) {
      this.isRefreshing = Boolean(status);
    },

    /**
     * Sets the loading state for authentication operations
     * Used to show loading indicators in UI during auth processes
     * @param {boolean} status - True for loading, false for idle
     */
    setLoading(status) {
      this.isLoading = Boolean(status);
    },

    /**
     * Clears the last authentication error from state
     * Useful for dismissing error messages in UI
     */
    clearError() {
      this.lastError = null;
    },

    /**
     * Initializes user state from stored tokens on application startup
     * Validates stored tokens and clears invalid/expired ones
     * Should be called once during app initialization
     */
    initializeUser() {
      if (!this.accessToken) {
        console.info('No stored access token found');
        return;
      }

      try {
        // Validate stored token format and content
        const decoded = decodeToken(this.accessToken);
        if (!decoded) {
          throw new Error('Invalid token format');
        }

        // Check if stored token has expired
        const now = Math.floor(Date.now() / 1000);
        if (decoded.exp && decoded.exp <= now) {
          console.warn('Stored access token has expired, clearing auth data');
          this.clearAuthData();
          return;
        }

        // Token is valid - extract and set user data
        this.decodeAndSetUser(this.accessToken);
        console.info('User initialized from stored token');
        
      } catch (error) {
        const authError = createAuthError(
          AUTH_ERRORS.TOKEN_DECODE_FAILED,
          'Failed to initialize user from stored token',
          error
        );
        
        this.lastError = authError;
        this.clearAuthData();
        console.error('Error initializing user:', authError);
      }
    },

    /**
     * Manually refreshes authentication tokens using the refresh token
     * Implements token refresh logic for maintaining user sessions
     * Note: Requires refreshAccessToken function to be implemented in authService
     * @returns {Promise<Object>} New token response from server
     * @throws {Object} Structured authentication error
     */
    async refreshTokens() {
      if (!this.refreshToken) {
        throw createAuthError(
          AUTH_ERRORS.LOGIN_FAILED,
          'No refresh token available'
        );
      }

      this.setRefreshing(true);
      try {
        // Dynamic import to avoid circular dependencies and code splitting
        const { refreshAccessToken } = await import('@/services/authService');
        const response = await refreshAccessToken(this.refreshToken);
        
        // Update tokens - use new refresh token if provided, otherwise keep existing
        this.setTokens(response.access_token, response.newRefreshToken || this.refreshToken);
        return response;
      } catch (error) {
        const authError = createAuthError(
          AUTH_ERRORS.LOGIN_FAILED,
          'Failed to refresh tokens',
          error
        );
        
        this.lastError = authError;
        this.clearAuthData(); // Clear invalid auth data
        throw authError;
      } finally {
        this.setRefreshing(false);
      }
    }
  },
});