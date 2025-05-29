<template>
  <div class="login-container">
    <!-- Page title, localized -->
    <h1>{{ t("login.title") }}</h1>

    <!-- Google OAuth login button component -->
    <GoogleLogin
      @credential-response="onGoogleCredential"
      @error="error = $event"
    />

    <!-- Display error messages if login fails -->
    <div v-if="error" class="mt-4 bg-red-100 p-2 rounded">
      <strong>{{ t("login.error_label") }}</strong> {{ error }}
    </div>

    <!-- Show backend response data when in debug mode -->
    <div v-if="DEBUG_MODE && responseData" class="mt-4 bg-blue-100 p-4 rounded">
      <h2 class="font-semibold mb-2">{{ t("login.backend_response") }}</h2>
      <ul class="text-sm">
        <li>
          <strong>{{ t("login.access_token") }}:</strong>
          {{ responseData.access_token }}
        </li>
        <li>
          <strong>{{ t("login.token_type") }}:</strong>
          {{ responseData.token_type }}
        </li>
      </ul>
      <p class="mt-2 text-sm text-gray-700">
        {{ t("login.backend_description") }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import { useAuthStore } from '@/services/authStore'; // Import Pinia auth store

import GoogleLogin from "@/components/auth/GoogleLogin.vue";
// loginWithGoogle and decodeToken are no longer directly used here, authStore handles it.

import "@/assets/styles/pages/login.css";

const { t } = useI18n();
const router = useRouter();
const authStore = useAuthStore(); // Instantiate the auth store

const DEBUG_MODE = import.meta.env.VITE_DEBUG_MODE === "true";

const error = ref(null);
const responseData = ref(null); // Holds the server response after login
// decoded ref is no longer needed here as user info comes from the store

// Detect user language for localization, default to English if not Hungarian
const userLang = navigator.language?.split("-")[0] === "hu" ? "hu" : "en";

/**
 * Handles the Google OAuth credential response.
 * Decodes the JWT token and sends it to backend for authentication.
 * Displays error messages or redirects on success.
 */
const onGoogleCredential = async (idToken) => {
  error.value = null;
  // The store's login action will handle decoding and setting user info.

  try {
    // Call the store action to login
    // authStore.isLoading can be used here if a loading indicator is desired
    const result = await authStore.login(idToken, userLang);
    responseData.value = result; // Store the raw response for debug mode if needed

    // Access user info via authStore.user or authStore.decodedAccessToken if needed
    // For example: console.log(authStore.user);

    if (!DEBUG_MODE) {
      router.push("/dailydraw"); // Redirect to protected route after successful login
    }
  } catch (err) {
    // The authStore.login action should throw an error, which is caught here.
    // The error might be from the API call or token handling within the store.
    console.error("Login failed in component:", err);
    error.value = err.message || t("login.auth_failed"); // Display a user-friendly message
  }
};
</script>
