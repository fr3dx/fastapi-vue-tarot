<template>
  <div class="home-container">
    <h1 class="text-2xl font-bold">Tarot App</h1>

    <!-- Two navigation links: daily draw and Google OAuth login -->
    <div class="links mt-4">
      <router-link to="/dialydraw" class="button-link">
        <button class="p-2 bg-blue-500 text-white rounded">Daily Card Draw</button>
      </router-link>

      <router-link to="/googleoauth" class="button-link ml-4">
        <button class="p-2 bg-green-500 text-white rounded">Google OAuth Login</button>
      </router-link>
    </div>

    <!-- Display error message if present -->
    <div v-if="error" class="mt-4 bg-red-100 p-2 rounded">
      <strong>Hiba:</strong> {{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const error = ref(null); // Reactive variable for optional error display

// Add custom error handling logic here if needed
</script>

<style scoped>
.home-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh;
}

.button-link {
  text-decoration: none;
}

button {
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

button:hover {
  background-color: #444;
}
</style>
