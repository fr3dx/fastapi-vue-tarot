<template>
  <div id="app-layout">
    <!-- Main application header -->
    <header>
      <nav>
        <!-- Navigation links (left side) -->
        <div>
          <router-link to="/" class="nav-link">{{ t("nav.home") }}</router-link>
          |
          <router-link to="/dailydraw" class="nav-link">{{ t("nav.daily_draw") }}</router-link>
        </div>

        <!-- Authentication section (right side) -->
        <div>
          <span v-if="authStore.isAuthenticated" class="auth-section">
            <span class="user-info">
              {{ t("nav.welcome", { name: authStore.user?.name || authStore.user?.email || 'User' }) }}
            </span>
            <button @click="handleLogout" class="btn btn-logout">
              {{ t("nav.logout") }}
            </button>
          </span>

          <span v-else>
            <router-link to="/login" class="btn btn-login">
              {{ t("nav.login") }}
            </router-link>
          </span>
        </div>
      </nav>
    </header>

    <!-- Main content area -->
    <main>
      <router-view />
    </main>

    <!-- Footer section -->
    <footer>
      <p>
        &copy; {{ new Date().getFullYear() }} {{ t("footer.company_name") }}.
        {{ t("footer.rights_reserved") }}
      </p>
    </footer>
  </div>
</template>

<script setup>
// Importing necessary hooks and stores
import { useAuthStore } from '@/services/authStore'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

const authStore = useAuthStore()
const router = useRouter()
const { t } = useI18n()

// Ensure user data is loaded if token exists (e.g., after page reload)
authStore.initializeUser()

// Logout handler: clear auth and redirect
const handleLogout = () => {
  authStore.logout() // Reset auth state in Pinia and localStorage
  router.push('/login') // Navigate to login screen
}
</script>

<style src="@/assets/App.css"></style>
