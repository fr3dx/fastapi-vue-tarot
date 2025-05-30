<template>
  <div class="home-container">
    <!-- Main page title, localized -->
    <h1 class="text-2xl font-bold">{{ t("home.title") }}</h1>

    <!-- Display error messages if any -->
    <div v-if="error" class="mt-4 bg-red-100 p-2 rounded">
      <strong>{{ t("home.error_label") }}</strong> {{ error }}
    </div>
  </div>
</template>

<script setup>
import "@/assets/styles/pages/home.css";
import { ref } from "vue";
import { useI18n } from "vue-i18n";

const { t } = useI18n();
const error = ref(null);
</script>
