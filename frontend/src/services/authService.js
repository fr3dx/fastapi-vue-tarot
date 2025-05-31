import axios from "axios";
import { jwtDecode } from "jwt-decode"; // Modern import syntax
import router from '@/router/router';

/**
 * Authentication service configuration constants
 * Centralizes all auth-related configuration including API endpoints and defaults
 */
const AUTH_CONFIG = {
  /** Base API URL from environment variables */
  API_URL: import.meta.env.VITE_APP_API_URL,
  
  /** Authentication API endpoints */
  ENDPOINTS: {
    GOOGLE_LOGIN: '/google',
    REFRESH_TOKEN: '/refresh',
  },
  
  /** Default language for authentication requests */
  DEFAULT_LANGUAGE: 'en',
};

/**
 * Validate required environment variables on module load
 * Fails fast if critical configuration is missing
 */
if (!AUTH_CONFIG.API_URL) {
  throw new Error('VITE_APP_API_URL environment variable is required');
}

/**
 * Determines if a URL is an authentication endpoint
 * Used to skip token validation for auth-related requests
 * @param {string} url - The URL to check
 * @returns {boolean} True if URL is an authentication endpoint
 */
const isAuthEndpoint = (url) => {
  const authEndpoints = Object.values(AUTH_CONFIG.ENDPOINTS);
  return authEndpoints.some(endpoint => url.includes(endpoint));
};

/**
 * Determines if a request is targeting our API
 * Used to decide whether to apply authentication headers
 * @param {string} url - The request URL to check
 * @returns {boolean} True if URL targets our API, false for external requests
 */
const isApiRequest = (url) => {
  try {
    // Extract base URL by removing the /api suffix
    const apiBase = AUTH_CONFIG.API_URL.substring(0, AUTH_CONFIG.API_URL.lastIndexOf("/api"));
    return url.startsWith(apiBase);
  } catch (error) {
    console.warn('Error checking API request:', error);
    return true; // Default to true for security - assume it's an API request
  }
};

/**
 * Creates a standardized service error object
 * Provides consistent error structure across all service methods
 * @param {string} type - Error type identifier
 * @param {string} message - Human-readable error message
 * @param {Error|null} originalError - Original error for debugging
 * @returns {Object} Structured error object with metadata
 */
const createServiceError = (type, message, originalError = null) => ({
  type,
  message,
  originalError,
  timestamp: new Date().toISOString(),
});

/**
 * Token Refresh Manager Class
 * Handles concurrent token refresh operations to prevent race conditions
 * Ensures only one refresh happens at a time while queuing other requests
 */
class TokenRefreshManager {
  constructor() {
    /** Flag to prevent concurrent refresh operations */
    this.isRefreshing = false;
    
    /** Queue of requests waiting for token refresh to complete */
    this.failedQueue = [];
  }

  /**
   * Processes all queued requests after refresh completes
   * Either resolves them with new token or rejects with error
   * @param {Error|null} error - Refresh error if failed
   * @param {string|null} token - New access token if successful
   */
  processQueue(error, token = null) {
    this.failedQueue.forEach(promise => {
      if (error) {
        promise.reject(error);
      } else {
        promise.resolve(token);
      }
    });
    this.failedQueue = [];
  }

  /**
   * Adds a new request to the waiting queue
   * Returns a promise that resolves when refresh completes
   * @returns {Promise} Promise that resolves with new token or rejects with error
   */
  queueRequest() {
    return new Promise((resolve, reject) => {
      this.failedQueue.push({ resolve, reject });
    });
  }

  /**
   * Executes token refresh operation with concurrency control
   * If refresh is already in progress, queues the request
   * @param {Function} refreshFunction - Function that performs the actual refresh
   * @returns {Promise<string>} Promise resolving to new access token
   */
  async executeRefresh(refreshFunction) {
    // If refresh is already in progress, queue this request
    if (this.isRefreshing) {
      return this.queueRequest();
    }

    this.isRefreshing = true;
    
    try {
      const newToken = await refreshFunction();
      this.processQueue(null, newToken);
      return newToken;
    } catch (error) {
      this.processQueue(error);
      throw error;
    } finally {
      this.isRefreshing = false;
    }
  }
}

/** Global token refresh manager instance - singleton pattern */
const tokenManager = new TokenRefreshManager();

/**
 * Authenticates user via Google OAuth token with backend API
 * Validates the Google ID token and exchanges it for access/refresh tokens
 * @param {string} idToken - Google OAuth ID token from client-side authentication
 * @param {string} lang - User's preferred language (optional, defaults to 'en')
 * @returns {Promise<Object>} Authentication response containing tokens and user data
 * @throws {Object} Structured service error with type and details
 */
export const loginWithGoogle = async (idToken, lang = AUTH_CONFIG.DEFAULT_LANGUAGE) => {
  // Input validation - check for required parameter
  if (!idToken) {
    throw createServiceError(
      'INVALID_INPUT',
      'Google ID token is required'
    );
  }

  // Validate token format and content
  if (typeof idToken !== 'string' || idToken.trim().length === 0) {
    throw createServiceError(
      'INVALID_INPUT',
      'Google ID token must be a non-empty string'
    );
  }

  try {
    // Make authentication request to backend
    const response = await axios.post(`${AUTH_CONFIG.API_URL}${AUTH_CONFIG.ENDPOINTS.GOOGLE_LOGIN}`, {
      token: idToken.trim(),
      lang: lang || AUTH_CONFIG.DEFAULT_LANGUAGE,
    }, {
      timeout: 10000, // 10 second timeout for auth requests
    });

    // Validate server response structure
    if (!response.data) {
      throw createServiceError(
        'INVALID_RESPONSE',
        'Empty response from authentication server'
      );
    }

    const { access_token, refresh_token, token_type } = response.data;
    
    // Ensure required tokens are present in response
    if (!access_token || !refresh_token) {
      throw createServiceError(
        'INVALID_RESPONSE',
        'Missing tokens in authentication response'
      );
    }

    console.info('Google authentication successful');
    return response.data;
    
  } catch (error) {
    console.error("Google authentication failed:", error);
    
    // Handle different error types with specific messaging
    if (error.response) {
      // Server responded with error status (4xx, 5xx)
      const serverError = createServiceError(
        'AUTH_SERVER_ERROR',
        error.response.data?.message || `Authentication failed with status ${error.response.status}`,
        error
      );
      throw serverError;
    } else if (error.request) {
      // Network error - request was made but no response received
      const networkError = createServiceError(
        'NETWORK_ERROR',
        'Unable to connect to authentication server',
        error
      );
      throw networkError;
    } else if (error.type) {
      // Already a structured error - pass through
      throw error;
    } else {
      // Unknown error type
      const genericError = createServiceError(
        'UNKNOWN_ERROR',
        error.message || 'Authentication failed',
        error
      );
      throw genericError;
    }
  }
};

/**
 * Requests a new access token using the refresh token
 * Handles token renewal when access token expires
 * @param {string} refreshToken - Valid refresh token for token renewal
 * @returns {Promise<Object>} Object containing new access token and optionally new refresh token
 * @throws {Object} Structured service error if refresh fails
 */
export const refreshAccessToken = async (refreshToken) => {
  if (!refreshToken) {
    throw createServiceError(
      'INVALID_INPUT',
      'Refresh token is required'
    );
  }

  try {
    // Request new tokens from backend
    const response = await axios.post(`${AUTH_CONFIG.API_URL}${AUTH_CONFIG.ENDPOINTS.REFRESH_TOKEN}`, {
      refresh_token: refreshToken,
    }, {
      timeout: 10000, // 10 second timeout for refresh requests
    });

    const { access_token, refresh_token: newRefreshToken } = response.data;

    // Validate response contains required access token
    if (!access_token) {
      throw createServiceError(
        'INVALID_RESPONSE',
        'No access token in refresh response'
      );
    }

    console.info('Token refresh successful');
    return { 
      access_token, 
      // If no new refresh token provided, keep the existing one
      newRefreshToken: newRefreshToken || refreshToken
    };

  } catch (error) {
    console.error("Token refresh failed:", error);
    
    // Handle specific refresh token expiration
    if (error.response?.status === 401) {
      throw createServiceError(
        'REFRESH_TOKEN_EXPIRED',
        'Refresh token has expired, please log in again',
        error
      );
    }
    
    // Pass through structured errors
    if (error.type) {
      throw error;
    }
    
    // Wrap other errors in standard format
    throw createServiceError(
      'REFRESH_FAILED',
      error.response?.data?.message || error.message || 'Token refresh failed',
      error
    );
  }
};

/**
 * Retrieves the current access token from the Pinia store
 * Uses dynamic import to avoid circular dependencies
 * @returns {Promise<string|null>} Current access token or null if not available
 */
export const getAccessToken = async () => {
  try {
    const { useAuthStore } = await import('@/services/authStore');
    const authStore = useAuthStore();
    return authStore.accessToken;
  } catch (error) {
    console.error('Error accessing auth store:', error);
    return null;
  }
};

/**
 * Decodes a JWT token to extract the payload
 * Safely handles malformed tokens and validation
 * @param {string} token - JWT token to decode
 * @returns {Object|null} Decoded token payload or null if invalid
 */
export const decodeToken = (token) => {
  if (!token || typeof token !== 'string') {
    return null;
  }

  try {
    const decoded = jwtDecode(token);
    
    // Basic token payload validation
    if (!decoded || typeof decoded !== 'object') {
      throw new Error('Invalid token payload');
    }
    
    return decoded;
  } catch (error) {
    console.error("Failed to decode token:", error);
    return null;
  }
};

/**
 * Checks if the current access token has expired
 * Compares token expiration time with current timestamp
 * @returns {Promise<boolean>} True if token is expired or invalid, false if valid
 */
export const isAccessTokenExpired = async () => {
  try {
    const token = await getAccessToken();
    if (!token) return true;

    const decoded = decodeToken(token);
    if (!decoded || !decoded.exp) return true;

    // Compare expiration time (in seconds) with current time
    const currentTime = Math.floor(Date.now() / 1000);
    const isExpired = decoded.exp < currentTime;
    
    if (isExpired) {
      console.warn('Access token has expired');
    }
    
    return isExpired;
  } catch (error) {
    console.error('Error checking token expiration:', error);
    return true; // Assume expired on error for security
  }
};

/**
 * Logs out the current user by clearing authentication data
 * Uses dynamic import to avoid circular dependencies
 */
export const logout = async () => {
  try {
    const { useAuthStore } = await import('@/services/authStore');
    const authStore = useAuthStore();
    authStore.logout();
    console.info('User logged out via service');
  } catch (error) {
    console.error('Error during logout:', error);
  }
};

/**
 * Checks if the user is currently authenticated
 * Uses dynamic import to avoid circular dependencies
 * @returns {Promise<boolean>} True if user is authenticated, false otherwise
 */
export const isAuthenticated = async () => {
  try {
    const { useAuthStore } = await import('@/services/authStore');
    const authStore = useAuthStore();
    return authStore.isAuthenticated;
  } catch (error) {
    console.error('Error checking authentication status:', error);
    return false;
  }
};

/**
 * Safely adds authentication token to request headers
 * Retrieves current token from store and adds Bearer authorization
 * @param {Object} config - Axios request configuration object
 * @returns {Promise<Object>} Modified request configuration with auth header
 */
const addTokenToRequest = async (config) => {
  try {
    const { useAuthStore } = await import('@/services/authStore');
    const authStore = useAuthStore();
    const token = authStore.accessToken;
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  } catch (error) {
    console.error('Error adding token to request:', error);
    return config;
  }
};

/**
 * Handles token refresh and request retry logic
 * Manages the complete token refresh flow including queue management
 * @param {Object} config - Axios request configuration object
 * @returns {Promise<Object>} Updated request configuration with new token
 * @throws {Error} If token refresh fails, clears auth data and redirects to login
 */
const handleTokenRefresh = async (config) => {
  try {
    const { useAuthStore } = await import('@/services/authStore');
    const authStore = useAuthStore();
    
    // Execute refresh through token manager to handle concurrency
    const refreshedToken = await tokenManager.executeRefresh(async () => {
      const result = await refreshAccessToken(authStore.refreshToken);
      authStore.setTokens(result.access_token, result.newRefreshToken);
      
      // Update default headers for future requests
      axios.defaults.headers.common.Authorization = `Bearer ${result.access_token}`;
      
      return result.access_token;
    });
    
    // Add refreshed token to current request
    config.headers.Authorization = `Bearer ${refreshedToken}`;
    return config;
    
  } catch (error) {
    console.error("Token refresh failed in interceptor:", error);
    
    // Clear authentication data and redirect to login on refresh failure
    const { useAuthStore } = await import('@/services/authStore');
    const authStore = useAuthStore();
    authStore.logout();
    
    // Redirect to login page if not already there
    if (router.currentRoute.value.path !== '/login') {
      router.push('/login');
    }
    
    throw error;
  }
};

/**
 * Axios Request Interceptor
 * Automatically handles token validation and refresh for outgoing requests
 * Skips authentication for auth endpoints and non-API requests
 */
axios.interceptors.request.use(
  async (config) => {
    try {
      // Skip token handling for authentication endpoints and external requests
      if (isAuthEndpoint(config.url) || !isApiRequest(config.url)) {
        return config;
      }

      // Check if current token has expired
      const tokenExpired = await isAccessTokenExpired();
      
      if (tokenExpired) {
        // Token expired - attempt refresh before making request
        return await handleTokenRefresh(config);
      } else {
        // Token is valid - add to request headers
        return await addTokenToRequest(config);
      }
      
    } catch (error) {
      console.error('Request interceptor error:', error);
      return Promise.reject(error);
    }
  },
  (error) => {
    console.error('Request interceptor setup error:', error);
    return Promise.reject(error);
  }
);

/**
 * Axios Response Interceptor
 * Handles 401 Unauthorized responses by attempting token refresh
 * Provides fallback token refresh for requests that weren't caught by request interceptor
 */
axios.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;

    // Handle 401 errors for API requests that haven't been retried yet
    if (error.response?.status === 401 && 
        !originalRequest._retry && 
        !isAuthEndpoint(originalRequest.url)) {
      
      // Mark request as retried to prevent infinite loops
      originalRequest._retry = true;

      try {
        console.warn('Received 401, attempting token refresh');
        await handleTokenRefresh(originalRequest);
        // Retry the original request with new token
        return axios(originalRequest);
      } catch (refreshError) {
        console.error('Token refresh failed in response interceptor');
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

/**
 * Axios Global Configuration
 * Sets default timeout and headers for all requests
 */
axios.defaults.timeout = 15000; // 15 second default timeout
axios.defaults.headers.common['Content-Type'] = 'application/json';

/**
 * Development Environment Logging
 * Provides detailed request/response logging in development mode
 * Helps with debugging authentication flows and API interactions
 */
if (process.env.NODE_ENV === 'development') {
  // Request logging interceptor
  axios.interceptors.request.use(request => {
    console.log('Starting Request:', {
      method: request.method?.toUpperCase(),
      url: request.url,
      hasAuth: !!request.headers.Authorization
    });
    return request;
  });

  // Response logging interceptor
  axios.interceptors.response.use(
    response => {
      console.log('Response:', {
        status: response.status,
        url: response.config.url
      });
      return response;
    },
    error => {
      console.log('Response Error:', {
        status: error.response?.status,
        url: error.config?.url,
        message: error.message
      });
      return Promise.reject(error);
    }
  );
}

export default axios;