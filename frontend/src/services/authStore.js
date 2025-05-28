import { defineStore } from 'pinia';
import { loginWithGoogle, decodeToken } from '@/services/authService'; // Assuming authService.js is in src/services

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: localStorage.getItem('access_token') || null,
    refreshToken: localStorage.getItem('refresh_token') || null,
    user: null, // Will be populated after decoding accessToken
    isLoading: false,
    isRefreshing: false, // For token refresh lock
  }),
  getters: {
    isAuthenticated: (state) => !!state.accessToken,
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
    async login(googleIdToken, language) {
      this.setLoading(true);
      try {
        const response = await loginWithGoogle(googleIdToken, language);
        if (response && response.access_token && response.refresh_token) {
          this.setTokens(response.access_token, response.refresh_token);
        }
        // Optionally, if you want to return the full response object
        return response; 
      } catch (error) {
        console.error('Login failed:', error);
        this.clearAuthData(); // Clear data on failed login
        throw error; // Re-throw the error to be caught by the caller
      } finally {
        this.setLoading(false);
      }
    },
    logout() {
      this.clearAuthData();
      // Consider router.push('/login') here or in the component
    },
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
    clearAuthData() {
      this.accessToken = null;
      this.refreshToken = null;
      this.user = null;
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    },
    setRefreshing(status) {
      this.isRefreshing = status;
    },
    setLoading(status) {
      this.isLoading = status;
    },
    // Initialize user from decoded token if accessToken exists on store setup
    // This can be called from App.vue or main.js when the store is first initialized
    initializeUser() {
      if (this.accessToken) {
        try {
          this.user = decodeToken(this.accessToken);
        } catch (error) {
          console.error('Error decoding token on initializeUser:', error);
          this.user = null;
          // If token decoding fails, it's invalid, so clear auth data
          this.clearAuthData(); 
        }
      }
    }
  },
});
