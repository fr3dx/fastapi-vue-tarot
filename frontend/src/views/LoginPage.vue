<template>
  <div class="p-4">
    <!-- Page title, localized -->
    <h1 class="text-xl font-bold mb-4">{{ t('login.title') }}</h1>

    <!-- Google OAuth login button component -->
    <GoogleLogin
      @credential-response="onGoogleCredential"
      @error="error = $event"
    />

    <!-- Display error messages if login fails -->
    <div v-if="error" class="mt-4 bg-red-100 p-2 rounded">
      <strong>{{ t('login.error_label') }}</strong> {{ error }}
    </div>

    <!-- Show backend response data when in debug mode -->
    <div v-if="DEBUG_MODE && responseData" class="mt-4 bg-blue-100 p-4 rounded">
      <h2 class="font-semibold mb-2">{{ t('login.backend_response') }}</h2>
      <ul class="text-sm">
        <li><strong>{{ t('login.access_token') }}:</strong> {{ responseData.access_token }}</li>
        <li><strong>{{ t('login.token_type') }}:</strong> {{ responseData.token_type }}</li>
        <li v-if="responseData.username">
          <strong>{{ t('login.username') }}:</strong> {{ responseData.username }}
        </li>
      </ul>
      <p class="mt-2 text-sm text-gray-700">{{ t('login.backend_description') }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';

import GoogleLogin from '@/components/auth/GoogleLogin.vue';
import { loginWithGoogle, decodeToken } from '@/services/authService'; // Import authentication services

const { t } = useI18n();
const router = useRouter();

const DEBUG_MODE = import.meta.env.VITE_DEBUG_MODE === 'true';

const error = ref(null);
const responseData = ref(null); // Holds the server response after login
const decoded = ref(null);

// Detect user language for localization, default to English if not Hungarian
const userLang = navigator.language?.split('-')[0] === 'hu' ? 'hu' : 'en';

/**
 * Handles the Google OAuth credential response.
 * Decodes the JWT token and sends it to backend for authentication.
 * Displays error messages or redirects on success.
 */
const onGoogleCredential = async (idToken) => {
  error.value = null;

  // Decode the JWT token to extract user info
  decoded.value = decodeToken(idToken);
  if (!decoded.value) {
    error.value = t('login.decode_failed');
    return;
  }

  try {
    // Call backend service to validate and login with Google token
    const result = await loginWithGoogle(idToken, userLang);
    responseData.value = result;

    if (!DEBUG_MODE) {
      router.push('/dailydraw'); // Redirect to protected route after successful login
    }
  } catch (err) {
    // Error handling - show user-friendly message
    error.value = t('login.auth_failed');
  }
};
</script>
