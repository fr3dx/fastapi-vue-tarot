// Main entry point of the Vue application

import { createApp } from "vue";
import { createPinia } from 'pinia';
import vue3GoogleLogin from 'vue3-google-login'; // Google OAuth login plugin
import App from "./App.vue";
import i18n from "./i18n"; // Internationalization plugin
import router from "./router/router"; // Vue Router instance

const app = createApp(App);
const pinia = createPinia();

app.use(router); // Register router plugin
app.use(i18n); // Register i18n plugin
app.use(pinia); // Register Pinia plugin

// Initialize vue3-google-login plugin with Google Client ID
// The Client ID is loaded from environment variables.
app.use(vue3GoogleLogin, {
  clientId: import.meta.env.VITE_GOOGLE_CLIENT_ID
});

app.mount("#app"); // Mount the app to the DOM element with id "app"
