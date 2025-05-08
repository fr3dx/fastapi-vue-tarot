import { createApp } from 'vue'
import App from './App.vue'
import router from './router.js' // <-- default import

const app = createApp(App)
app.use(router)
app.mount('#app')


