// Vue Router setup with authentication guard for protected routes
import { createRouter, createWebHistory } from "vue-router";
import Home from "@/views/Home.vue";
import DailyDraw from "@/views/DailyDraw.vue";
import LoginPage from "@/views/LoginPage.vue";

/**
 * Navigation guard to protect routes requiring authentication.
 * Updated to handle async authentication check.
 */
const requireAuth = async (to, from, next) => {
  try {
    // Dinamikusan importáljuk az auth store-t a circular dependency elkerülésére
    const { useAuthStore } = await import("@/services/authStore");
    const authStore = useAuthStore();
    
    // Ellenőrizzük hogy a store inicializálva van-e
    if (!authStore.user && authStore.accessToken) {
      // Ha van token de nincs user, inicializáljuk
      authStore.initializeUser();
    }
    
    // Ellenőrizzük az authentication státuszt
    if (authStore.isAuthenticated) {
      console.info(`Access granted to ${to.path}`);
      next(); // User is authenticated, proceed to the route
    } else {
      console.warn(`Access denied to ${to.path}, redirecting to login`);
      next("/login"); // Not authenticated, redirect to login page
    }
  } catch (error) {
    console.error("Error in auth guard:", error);
    // Hiba esetén is átirányítunk a login oldalra
    next("/login");
  }
};

/**
 * Opcionális: Megakadályozza hogy már bejelentkezett user a login oldalra menjen
 */
const redirectIfAuthenticated = async (to, from, next) => {
  try {
    const { useAuthStore } = await import("@/services/authStore");
    const authStore = useAuthStore();
    
    // Inicializáljuk a user-t ha szükséges
    if (!authStore.user && authStore.accessToken) {
      authStore.initializeUser();
    }
    
    if (authStore.isAuthenticated) {
      console.info("User already authenticated, redirecting to daily draw");
      next("/dailydraw"); // Már be van jelentkezve, átirányítás a daily draw oldalra
    } else {
      next(); // Nincs bejelentkezve, mehet a login oldalra
    }
  } catch (error) {
    console.error("Error in login redirect guard:", error);
    next(); // Hiba esetén engedjük tovább
  }
};

const routes = [
  { 
    path: "/", 
    name: "Home", 
    component: Home 
  },
  {
    path: "/dailydraw",
    name: "DailyDraw",
    component: DailyDraw,
    beforeEnter: requireAuth, // Protect this route with auth guard
  },
  { 
    path: "/login", 
    name: "Login", 
    component: LoginPage,
    beforeEnter: redirectIfAuthenticated, // Redirect if already logged in
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Globális navigation guard a teljes app szintű ellenőrzéshez
router.beforeEach(async (to, from, next) => {
  try {
    // Inicializáljuk az auth store-t az első navigációnál
    const { useAuthStore } = await import("@/services/authStore");
    const authStore = useAuthStore();
    
    // Ha van stored token de nincs user, inicializáljuk
    if (!authStore.user && authStore.accessToken && !authStore.isLoading) {
      console.info("Initializing user from stored token");
      authStore.initializeUser();
    }
    
    // Folytatjuk a normál route guard logikával
    next();
  } catch (error) {
    console.error("Error in global navigation guard:", error);
    next();
  }
});

// Opcionális: Navigation után logolás
router.afterEach((to, from) => {
  console.info(`Navigated from ${from.path || 'initial'} to ${to.path}`);
});

export default router;