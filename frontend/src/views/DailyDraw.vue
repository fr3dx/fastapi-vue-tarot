<template>
  <div class="draw-container">
    <h1>{{ t('dailyDraw.title') }}</h1>

    <!-- Show login prompt if user is not authenticated -->
    <div v-if="!isAuthenticated">
      <p>{{ t('dailyDraw.login_prompt') }}</p>
      <router-link to="/googleoauth">
        <button class="p-2 bg-green-500 text-white rounded">
          {{ t('dailyDraw.login_button') }}
        </button>
      </router-link>
    </div>

    <!-- Show card draw interface if user is authenticated -->
    <div v-else>
      <button @click="drawCard" :disabled="loading">
        <span v-if="!loading">{{ t('dailyDraw.draw_button') }}</span>
        <span v-else>{{ t('dailyDraw.loading') }}</span>
      </button>

      <!-- Display error message -->
      <p v-if="errorMessage" class="text-red-500 mt-2">{{ errorMessage }}</p>

      <!-- Display drawn card and description -->
      <div v-if="card" class="card-display">
        <img :src="card.image_url" width="300" height="527" :alt="t('dailyDraw.card_alt')" />
        <p class="card-name">{{ card.name }}</p>

        <!-- Button to reveal card description -->
        <button v-if="!description" @click="revealDescription">
          {{ t('dailyDraw.show_description') }}
        </button>
        <p class="card-description" v-if="description">{{ description }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
// Vue and libraries
import { ref, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import axios from 'axios';
import '@/assets/DailyDraw.css';

// Localization instance
const { t, locale } = useI18n();

// Reactive state variables
const card = ref(null);            // Stores drawn card details
const errorMessage = ref(null);    // Stores error messages for user feedback
const loading = ref(false);        // Loading state for async calls
const description = ref(null);     // Card description text
const isAuthenticated = ref(false); // User authentication status

// Retrieve token from localStorage on component mount
const getToken = () => localStorage.getItem('access_token');

// Backend URL from environment variables
const backendUrl = import.meta.env.VITE_BACKEND_URL;

/**
 * Checks if user is authenticated based on presence of JWT token.
 */
const checkAuthentication = () => {
  isAuthenticated.value = !!getToken();
};

// Run authentication check when component mounts
onMounted(() => {
  checkAuthentication();
});

/**
 * Draw a daily card from the backend API.
 * Includes JWT token in Authorization header.
 */
const drawCard = async () => {
  if (loading.value) return; // Prevent multiple simultaneous requests
  loading.value = true;
  description.value = null; // Reset description on new draw
  errorMessage.value = null;

  try {
    const token = getToken();
    const response = await axios.get(`${backendUrl}/api/daily_card`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    card.value = response.data;

    // Fetch localized card name
    const res = await fetch(`${backendUrl}/api/card_description/${card.value.key}?lang=${locale.value}`);
    if (res.ok) {
      const data = await res.json();
      card.value.name = data.name ?? card.value.name;
    }
  } catch (e) {
    console.error('Draw error:', e);
    card.value = null;

    if (e.response?.status === 403) {
      errorMessage.value = t('dailyDraw.error_already_drawn');
    } else {
      errorMessage.value = t('dailyDraw.error_general');
    }
  } finally {
    loading.value = false;
  }
};

/**
 * Reveal and fetch localized description of the drawn card.
 */
const revealDescription = async () => {
  if (!card.value?.key) return;

  try {
    const res = await fetch(`${backendUrl}/api/card_description/${card.value.key}?lang=${locale.value}`);
    if (!res.ok) throw new Error('Description fetch failed');

    const data = await res.json();
    card.value.name = data.name ?? card.value.name;
    description.value = data.description;
  } catch (e) {
    console.error('Description error:', e);
    description.value = t('dailyDraw.description_error');
  }
};
</script>
