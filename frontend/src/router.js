import { createRouter, createWebHistory } from 'vue-router';
import Home from './Home.vue';
import DialyDraw from './DialyDraw.vue';
import GoogleOauth from './GoogleOauth.vue'; // Google OAuth2 login page

// Authentication check function
const isAuthenticated = () => {
  return !!localStorage.getItem('access_token'); // Check if access token exists
};

// Navigation guard to protect authenticated routes
const requireAuth = (to, from, next) => {
  if (isAuthenticated()) {
    next(); // Allow access if authenticated
  } else {
    next('/googleoauth'); // Redirect to login if not authenticated
  }
};

// Route configuration
const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/dialydraw', name: 'DialyDraw', component: DialyDraw, beforeEnter: requireAuth },
  { path: '/googleoauth', name: 'GoogleOauth', component: GoogleOauth },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
