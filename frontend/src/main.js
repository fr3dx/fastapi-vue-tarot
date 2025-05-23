// Main entry point of the Vue application

import { createApp } from 'vue';
import App from './App.vue';
import i18n from './i18n'; // Internationalization plugin
import router from './router/router'; // Vue Router instance
import vue3GoogleLogin from 'vue3-google-login';

const app = createApp(App);

app.use(router); // Register router plugin
app.use(i18n);   // Register i18n plugin
app.use(vue3GoogleLogin, {
  clientId: '928275508669-tf20bv090ega6llrvcp57ct6v74d5me9.apps.googleusercontent.com',
});

app.mount('#app'); // Mount the app to the DOM element with id "app"
