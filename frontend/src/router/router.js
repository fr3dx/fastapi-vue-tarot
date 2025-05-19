// Vue Router setup with authentication guard for protected routes

import { createRouter, createWebHistory } from 'vue-router';
import Home from '@/views/Home.vue';
import DailyDraw from '@/views/DailyDraw.vue';
import LoginPage from '@/views/LoginPage.vue';
import { isAuthenticated } from '@/services/authService'; // Import authentication utility

/**
 * Navigation guard to protect routes requiring authentication.
 * If the user is not authenticated, redirect to the login page.
 */
const requireAuth = (to, from, next) => {
  if (isAuthenticated()) {
    next(); // User is authenticated, proceed to the route
  } else {
    next('/login'); // Not authenticated, redirect to login page
  }
};

const routes = [
  { path: '/', name: 'Home', component: Home },
  {
    path: '/dailydraw',
    name: 'DailyDraw',
    component: DailyDraw,
    beforeEnter: requireAuth, // Protect this route with auth guard
  },
  { path: '/login', name: 'Login', component: LoginPage },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
