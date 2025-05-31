// Main entry point of the Vue application
import { createApp } from "vue";
import { createPinia } from 'pinia';
import vue3GoogleLogin from 'vue3-google-login'; // Google OAuth login plugin
import App from "./App.vue";
import i18n from "./i18n"; // Internationalization plugin
import router from "./router/router"; // Vue Router instance

// Create Vue app instance
const app = createApp(App);
const pinia = createPinia();

// Register plugins
app.use(pinia); // Register Pinia plugin first (important for store usage)
app.use(router); // Register router plugin
app.use(i18n); // Register i18n plugin

// Initialize vue3-google-login plugin with Google Client ID
// The Client ID is loaded from environment variables.
const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;

if (!googleClientId) {
  console.error('VITE_GOOGLE_CLIENT_ID environment variable is not set');
} else {
  app.use(vue3GoogleLogin, {
    clientId: googleClientId
  });
}

// Initialize auth store after Pinia is registered
const initializeAuth = async () => {
  try {
    const { useAuthStore } = await import("@/services/authStore");
    const authStore = useAuthStore();
    
    // Initialize user from stored tokens if available
    authStore.initializeUser();
    
    console.info("Auth store initialized successfully");
  } catch (error) {
    console.error("Failed to initialize auth store:", error);
  }
};

// Mount the app and initialize auth
app.mount("#app");

// Initialize auth after app is mounted
initializeAuth();