// Main entry point of the Vue application

import { createApp } from 'vue';
import App from './App.vue';
import i18n from './i18n'; // Internationalization plugin
import router from './router/router'; // Vue Router instance

const app = createApp(App);

app.use(router); // Register router plugin
app.use(i18n);   // Register i18n plugin

app.mount('#app'); // Mount the app to the DOM element with id "app"
