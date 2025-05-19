<template>
  <div class="home-container">
    <!-- Main title of the application -->
    <h1 class="text-2xl font-bold">{{ t('home.title') }}</h1>

    <!-- Navigation buttons: daily draw and Google OAuth login -->
    <div class="links mt-4">
      <router-link to="/dailydraw" class="button-link">
        <button class="p-2 bg-blue-500 text-white rounded">
          {{ t('home.dailyDraw') }}
        </button>
      </router-link>

      <router-link to="/googleoauth" class="button-link ml-4">
        <button class="p-2 bg-green-500 text-white rounded">
          {{ t('home.login') }}
        </button>
      </router-link>
    </div>

    <!-- Display error message if present -->
    <div v-if="error" class="mt-4 bg-red-100 p-2 rounded">
      <strong>{{ t('home.error_label') }}</strong> {{ error }}
    </div>
  </div>
</template>

<script setup>
// Import Vue composition API and localization
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

// Internationalization function
const { t } = useI18n()

// Reactive variable for error messages
const error = ref(null)

// You may add custom error-handling logic here later
</script>

<style scoped>
/* Center the container vertically and horizontally */
.home-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh;
}

/* Remove underline from router-links */
.button-link {
  text-decoration: none;
}

/* Styling for all buttons */
button {
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

/* Hover effect for buttons */
button:hover {
  background-color: #444;
}
</style>
