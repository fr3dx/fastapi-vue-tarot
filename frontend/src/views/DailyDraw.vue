<template>
  <div class="draw-container">
    <h1>{{ t("dailyDraw.title") }}</h1>

    <!-- Prompt user to log in if not authenticated -->
    <div v-if="!authStore.isAuthenticated">
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

import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import { useAuthStore } from '@/services/authStore'
import '@/assets/styles/pages/dailydraw.css'

// Initialize i18n translation and reactive locale properties
const { t, locale } = useI18n()

// Initialize the authentication store
const authStore = useAuthStore()

// Reactive references to hold the current card, error messages, loading state, and card description
const card = ref(null)              // Holds the drawn card data
const errorMessage = ref(null)     // Stores error messages for UI display
const loading = ref(false)         // Indicates if an API request is in progress
const description = ref(null)      // Holds the localized description of the drawn card

// Backend API base URL loaded from environment variables
const backendUrl = import.meta.env.VITE_BACKEND_URL

// Initialize user authentication state on component mount
onMounted(() => {
  authStore.initializeUser()
})

/**
 * Initiates fetching of the daily card from the backend API.
 * Manages loading state, resets relevant reactive variables,
 * and handles errors by displaying user-friendly messages.
 */
const drawCard = async () => {
  if (loading.value) return // Prevent multiple simultaneous requests

  // Reset UI state before starting the API call
  loading.value = true
  errorMessage.value = null
  card.value = null
  description.value = null

  try {
    // Request the daily card data from the API
    const response = await axios.get(`${backendUrl}/api/daily_card`)
    card.value = response.data

    // Fetch localized card name using the card key and current locale
    const { data } = await axios.get(
      `${backendUrl}/api/card_description/${card.value.key}?lang=${locale.value}`
    )

    // Update card name with localized version if available
    card.value.name = data.name ?? card.value.name
  } catch (error) {
    // Log the error for debugging purposes
    console.error('Card draw failed:', error)
    card.value = null

    // Provide specific error messages based on response status
    if (error.response?.status === 403) {
      errorMessage.value = t('dailyDraw.error_already_drawn')
    } else {
      errorMessage.value = t('dailyDraw.error_general')
    }
  } finally {
    // Reset loading state regardless of success or failure
    loading.value = false
  }
}

/**
 * Fetches and reveals the localized description of the drawn card.
 * Should only be called after a card has been drawn successfully.
 * Handles errors by displaying a fallback error message.
 */
const revealDescription = async () => {
  if (!card.value?.key) return // Exit early if no card has been drawn

  try {
    // Request the card description based on card key and current locale
    const { data } = await axios.get(
      `${backendUrl}/api/card_description/${card.value.key}?lang=${locale.value}`
    )

    // Update the card name and description if localized data is available
    card.value.name = data.name ?? card.value.name
    description.value = data.description
  } catch (error) {
    // Log error and display fallback message to user
    console.error('Failed to load card description:', error)
    description.value = t('dailyDraw.description_error')
  }
}
</script>
