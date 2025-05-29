<template>
  <div class="draw-container">
    <h1>{{ t("dailyDraw.title") }}</h1>

    <!-- Prompt user to log in if not authenticated -->
    <div v-if="!isAuthenticated" class="auth-prompt">
      <p>{{ t("dailyDraw.login_prompt") }}</p>
      <router-link to="/googleoauth" class="btn btn-login">
        {{ t("dailyDraw.login_button") }}
      </router-link>
    </div>

    <!-- Daily card draw interface for authenticated users -->
    <div v-else>
      <button @click="drawCard" :disabled="loading" class="btn btn-draw">
        <span v-if="!loading">{{ t("dailyDraw.draw_button") }}</span>
        <span v-else>{{ t("dailyDraw.loading") }}</span>
      </button>

      <!-- Show any error messages -->
      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

      <!-- Display drawn card and optional description -->
      <div v-if="card" class="card-display">
        <img
          :src="card.image_url"
          width="300"
          height="527"
          :alt="t('dailyDraw.card_alt')"
        />
        <p class="card-name">{{ card.name }}</p>

        <!-- Show "Reveal Description" button if description not yet revealed -->
        <button
          v-if="!description"
          @click="revealDescription"
          class="btn btn-description"
        >
          {{ t("dailyDraw.show_description") }}
        </button>

        <!-- Show card description once revealed -->
        <p v-if="description" class="card-description">
          {{ description }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
// Import Vue Composition API functions
import { ref, onMounted } from 'vue'
// Internationalization composable
import { useI18n } from 'vue-i18n'
// HTTP client for API calls
import axios from 'axios'
// Import component styles
import '@/assets/styles/pages/dailydraw.css'

// Setup i18n translation function and reactive locale
const { t, locale } = useI18n()

// Reactive state variables
const card = ref(null)              // Stores the currently drawn card data
const errorMessage = ref(null)     // Holds any error messages to display to the user
const loading = ref(false)         // Indicates if a card draw request is in progress
const description = ref(null)      // Stores the localized description of the drawn card
const isAuthenticated = ref(false) // Tracks if the user is logged in/authenticated

// Backend API base URL from environment variables
const backendUrl = import.meta.env.VITE_BACKEND_URL

/**
 * Check user authentication status by verifying the presence of a local access token.
 * Note: This is a basic check; token validation should be handled more securely globally,
 * for example in router guards or Axios interceptors.
 */
const checkAuthentication = () => {
  const token = localStorage.getItem('access_token')
  isAuthenticated.value = !!token
}

// Check authentication status when component mounts
onMounted(() => {
  checkAuthentication()
})

/**
 * Fetches the daily card data from the backend API.
 * Manages loading state and error handling.
 * Updates the card reactive variable with the fetched data.
 */
const drawCard = async () => {
  if (loading.value) return // Prevent concurrent requests

  // Reset state before API call
  loading.value = true
  errorMessage.value = null
  card.value = null
  description.value = null

  try {
    // Request daily card data
    const response = await axios.get(`${backendUrl}/api/daily_card`)
    card.value = response.data

    // Fetch localized card name based on current locale
    const { data } = await axios.get(
      `${backendUrl}/api/card_description/${card.value.key}?lang=${locale.value}`
    )

    // Override card name with localized version if available
    card.value.name = data.name ?? card.value.name
  } catch (error) {
    console.error('Card draw failed:', error)
    card.value = null

    // Show specific error messages depending on the response
    if (error.response?.status === 403) {
      errorMessage.value = t('dailyDraw.error_already_drawn')
    } else {
      errorMessage.value = t('dailyDraw.error_general')
    }
  } finally {
    loading.value = false
  }
}

/**
 * Fetches and displays the localized description of the drawn card.
 * Should only be called after a card has been successfully drawn.
 */
const revealDescription = async () => {
  if (!card.value?.key) return

  try {
    // Request card description from backend based on card key and locale
    const { data } = await axios.get(
      `${backendUrl}/api/card_description/${card.value.key}?lang=${locale.value}`
    )

    // Update card name and description, if provided
    card.value.name = data.name ?? card.value.name
    description.value = data.description
  } catch (error) {
    console.error('Failed to load card description:', error)
    // Display fallback error message in UI
    description.value = t('dailyDraw.description_error')
  }
}
</script>
