<template>
  <div id="app-layout" class="min-h-screen bg-gray-100">
    <header class="bg-blue-600 text-white shadow-md">
      <nav class="container mx-auto px-6 py-3 flex justify-between items-center">
        <div>
          <router-link to="/" class="hover:text-blue-200">{{ t("nav.home") }}</router-link> |
          <router-link to="/dailydraw" class="hover:text-blue-200">{{ t("nav.daily_draw") }}</router-link>
        </div>
        <div>
          <span v-if="authStore.isAuthenticated" class="flex items-center">
            <span class="mr-4">{{ t("nav.welcome", { name: authStore.user?.name || authStore.user?.email || 'User' }) }}</span>
            <button @click="handleLogout" class="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded">
              {{ t("nav.logout") }}
            </button>
          </span>
          <span v-else>
            <router-link to="/login" class="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded">
              {{ t("nav.login") }}
            </router-link>
          </span>
        </div>
      </nav>
    </header>
    <main class="container mx-auto p-6">
      <router-view />
    </main>
    <footer class="bg-gray-800 text-white text-center p-4 mt-8">
      <p>&copy; {{ new Date().getFullYear() }} {{ t("footer.company_name") }}. {{ t("footer.rights_reserved") }}</p>
    </footer>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/services/authStore';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n'; // Import useI18n

const authStore = useAuthStore();
const router = useRouter();
const { t } = useI18n(); // Initialize t function for translations

// Call initializeUser on app load to ensure user state is set if token exists
// This is important if the user reloads the page and has a valid token in localStorage.
// The store itself loads tokens from localStorage, but this action ensures 'user' object is populated.
authStore.initializeUser(); 

const handleLogout = () => {
  authStore.logout(); // This clears tokens and user state in Pinia and localStorage
  router.push('/login'); // Redirect to login page
};
</script>

<style>
/* Basic styling, can be expanded or moved to a CSS file */
#app-layout nav a {
  margin-right: 10px;
  text-decoration: none;
}

#app-layout nav a.router-link-exact-active {
  font-weight: bold;
  color: #cce5ff; /* A lighter blue for active links */
}
</style>
