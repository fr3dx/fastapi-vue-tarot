<template>
  <div class="app-container">
    <h1>Tarot kártyahúzás</h1>

    <button @click="drawCard" :disabled="loading">
      <span v-if="!loading">Húzz egy kártyát</span>
      <span v-else>Töltés…</span>
    </button>

    <div v-if="card" class="card-display">
      <img :src="backendUrl + card.image_url" width="300" height="527" alt="Kártya kép" />
      <p class="card-name">{{ card.name }}</p>

      <button v-if="!description" @click="revealDescription">Mutasd a jelentését</button>
      <p class="card-description" v-if="description">{{ description }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const card = ref(null)
const loading = ref(false)
const description = ref(null)
const backendUrl = 'http://localhost:8000'

async function drawCard() {
  if (loading.value) return
  loading.value = true
  description.value = null // reset description
  try {
    const res = await fetch(`${backendUrl}/api/daily_card`)
    if (!res.ok) throw new Error('API hiba: ' + res.status)
    const data = await res.json()
    card.value = data
  } catch (e) {
    console.error('Hiba történt:', e)
    card.value = null
  } finally {
    loading.value = false
  }
}

async function revealDescription() {
  if (!card.value?.key) return
  try {
    const res = await fetch(`${backendUrl}/api/card_description/${card.value.key}`);
    if (!res.ok) throw new Error('Leírás lekérése hiba: ' + res.status);
    const data = await res.json();
    description.value = data.description;
  } catch (e) {
    console.error('Leírás hiba:', e);
    description.value = "Nem sikerült betölteni a leírást.";
  }
}
</script>


<style scoped>
.app-container {
  text-align: center;
  padding: 2rem;
  font-family: sans-serif;
}

button {
  margin-bottom: 1rem;
  padding: 0.5rem 1.2rem;
  font-size: 1rem;
  cursor: pointer;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.card-display {
  margin-top: 1rem;
}

.card-name {
  margin-top: 0.5rem;
  font-size: 1.2rem;
  font-weight: bold;
}

.card-description {
  font-size: 0.9rem;
  color: #444;
  margin-top: 0.5rem;
}
</style>
