<template>
  <div class="draw-container">
    <h1>{{ t("dailyDraw.title") }}</h1>

    <!-- Show login prompt if user is not authenticated -->
    <div v-if="!isAuthenticated">
      <p>{{ t("dailyDraw.login_prompt") }}</p>
      <router-link to="/googleoauth">
        <button class="p-2 bg-green-500 text-white rounded">
          {{ t("dailyDraw.login_button") }}
        </button>
      </router-link>
    </div>

    <!-- Show card draw interface if user is authenticated -->
    <div v-else>
      <button @click="drawCard" :disabled="loading">
        <span v-if="!loading">{{ t("dailyDraw.draw_button") }}</span>
        <span v-else>{{ t("dailyDraw.loading") }}</span>
      </button>

      <!-- Display error message -->
      <p v-if="errorMessage" class="text-red-500 mt-2">{{ errorMessage }}</p>

      <!-- Display drawn card and description -->
      <div v-if="card" class="card-display">
        <img
          :src="card.image_url"
          width="300"
          height="527"
          :alt="t('dailyDraw.card_alt')"
        />
        <p class="card-name">{{ card.name }}</p>

        <!-- Button to reveal card description -->
        <button v-if="!description" @click="revealDescription">
          {{ t("dailyDraw.show_description") }}
        </button>
        <p class="card-description" v-if="description">{{ description }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
// Vue and third-party imports
import { ref, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import axios from 'axios';
import '@/assets/DailyDraw.css';

// Localization instance
const { t, locale } = useI18n();

// Reactive state variables
const card = ref(null);            // Holds the drawn card's details
const errorMessage = ref(null);    // Message to display in case of error
const loading = ref(false);        // Indicates whether a request is in progress
const description = ref(null);     // Holds the card's localized description
const isAuthenticated = ref(false); // Tracks whether the user is authenticated

// Backend base URL from environment variables
const backendUrl = import.meta.env.VITE_BACKEND_URL;

/**
 * Determines authentication status based on the presence of access token.
 * Note: Token validation logic should be handled globally (e.g., in an interceptor).
 */
const checkAuthentication = () => {
  const token = localStorage.getItem('access_token');
  isAuthenticated.value = !!token;
};

// Run authentication check on component mount
onMounted(() => {
  checkAuthentication();
});

/**
 * Sends a request to the backend to draw a daily card.
 * Uses Axios, which will include an Authorization header via interceptor if available.
 */
const drawCard = async () => {
  if (loading.value) return; // Prevent overlapping requests
  loading.value = true;
  errorMessage.value = null;
  card.value = null;
  description.value = null;

  try {
    // Request the daily card from the backend
    const response = await axios.get(`${backendUrl}/api/daily_card`);
    card.value = response.data;

    // Request localized card name using Axios
    const { data } = await axios.get(
      `${backendUrl}/api/card_description/${card.value.key}?lang=${locale.value}`
    );

    // Fallback to default name if localization is unavailable
    card.value.name = data.name ?? card.value.name;

  } catch (error) {
    console.error('Card draw failed:', error);
    card.value = null;

    // Handle specific error codes
    if (error.response?.status === 403) {
      errorMessage.value = t('dailyDraw.error_already_drawn');
    } else {
      errorMessage.value = t('dailyDraw.error_general');
    }
  } finally {
    loading.value = false;
  }
};

/**
 * Fetches and reveals the localized description of the drawn card.
 * Should only be called after a card has been drawn.
 */
const revealDescription = async () => {
  if (!card.value?.key) return;

  try {
    const { data } = await axios.get(
      `${backendUrl}/api/card_description/${card.value.key}?lang=${locale.value}`
    );

    // Update name and description if data is available
    card.value.name = data.name ?? card.value.name;
    description.value = data.description;

  } catch (error) {
    console.error('Failed to load card description:', error);
    description.value = t('dailyDraw.description_error');
  }
};
</script>
