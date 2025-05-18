<template>
  <div class="draw-container">
    <h1>Napi Kártyahúzás</h1>

    <!-- Show login prompt if user is not authenticated -->
    <div v-if="!isAuthenticated">
      <p>Be kell jelentkezned, hogy húzhass egy kártyát!</p>
      <router-link to="/googleoauth">
        <button class="p-2 bg-green-500 text-white rounded">Jelentkezz be Google-lel</button>
      </router-link>
    </div>

    <!-- Show card draw interface if user is authenticated -->
    <div v-else>
      <button @click="drawCard" :disabled="loading">
        <span v-if="!loading">Húzz egy kártyát</span>
        <span v-else>Töltés…</span>
      </button>

      <!-- Error Message for daily 1 card draw -->
      <p v-if="errorMessage" class="text-red-500 mt-2">{{ errorMessage }}</p>

      <!-- Display drawn card and description -->
      <div v-if="card" class="card-display">
        <img :src="card.image_url" width="300" height="527" alt="Kártya kép" />
        <p class="card-name">{{ card.name }}</p>

        <!-- Button to reveal card description -->
        <button v-if="!description" @click="revealDescription">Mutasd a jelentését</button>
        <p class="card-description" v-if="description">{{ description }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import '@/assets/DialyDraw.css';

const card = ref(null);
const errorMessage = ref(null);
const loading = ref(false);
const description = ref(null);
const isAuthenticated = ref(false);
const backendUrl = import.meta.env.VITE_BACKEND_URL;
const token = localStorage.getItem('access_token');

const checkAuthentication = () => {
  isAuthenticated.value = !!token;
};

onMounted(() => {
  checkAuthentication();
});

const drawCard = async () => {
  if (loading.value) return;
  loading.value = true;
  description.value = null;
  errorMessage.value = null;

  try {
    const response = await axios.get(`${backendUrl}/api/daily_card`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    card.value = response.data;
  } catch (e) {
    console.error('Hiba történt:', e);
    card.value = null;

    if (e.response?.status === 403) {
      errorMessage.value = "Ma már húztál kártyát! Holnap újra próbálhatod.";
    } else {
      errorMessage.value = "Hiba történt a kártyahúzás közben.";
    }
  } finally {
    loading.value = false;
  }
};

const revealDescription = async () => {
  if (!card.value?.key) return;

  const userLang = navigator.language.slice(0, 2) || 'hu';

  try {
    const res = await fetch(`${backendUrl}/api/card_description/${card.value.key}?lang=${userLang}`);
    if (!res.ok) throw new Error('Leírás hiba: ' + res.status);
    const data = await res.json();
    description.value = data.description;
  } catch (e) {
    console.error('Leírás hiba:', e);
    description.value = "Nem sikerült betölteni a leírást.";
  }
};

</script>