<template>
  <div class="home-container">
    <!-- Main page title, localized -->
    <h1 class="text-2xl font-bold">{{ t('home.title') }}</h1>

    <!-- Navigation buttons to daily draw and login -->
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

    <!-- Display error messages if any -->
    <div v-if="error" class="mt-4 bg-red-100 p-2 rounded">
      <strong>{{ t('home.error_label') }}</strong> {{ error }}
    </div>
  </div>
</template>

<script setup>
import '@/assets/Home.css';

import { ref } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
const error = ref(null);
</script>
