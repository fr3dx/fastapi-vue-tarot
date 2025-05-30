<template>
  <div class="login-container">
    <!-- Page title, localized -->
    <h1>{{ t("login.title") }}</h1>

    <!-- 
      GoogleLoginButton component.
      The 'onSuccessCallback' prop is bound to the onGoogleCredential method 
      to handle the response after a successful Google login, centralizing 
      the logic in the parent component while keeping the button itself reusable.
    -->
    <GoogleLoginButton :onSuccessCallback="onGoogleCredential" />

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
import { useAuthStore } from '@/services/authStore'; // Assuming authStore path is correct
import GoogleLoginButton from "@/components/GoogleLoginButton.vue"; // Import the new component
import "@/assets/styles/pages/login.css";

const { t } = useI18n();
const router = useRouter();
const authStore = useAuthStore(); // Instantiate the auth store

const DEBUG_MODE = import.meta.env.VITE_DEBUG_MODE === "true";

const error = ref(null);
const responseData = ref(null); // Holds the server response after login

// Detect user language for localization, default to English if not Hungarian
const userLang = navigator.language?.split("-")[0] === "hu" ? "hu" : "en";

/**
 * Handles the Google OAuth credential response.
 * This function is passed as a prop to the GoogleLoginButton component.
 * It receives the CredentialResponse object from vue3-google-login.
 * Decodes the JWT token and sends it to backend for authentication.
 * Displays error messages or redirects on success.
 * @param {Object} credentialResponse - The response object from Google OAuth.
 */
const onGoogleCredential = async (credentialResponse) => {
  error.value = null;
  // The store's login action will handle decoding and setting user info.

  try {
    // Call the store action to login, passing the ID token string from the response.
    // authStore.isLoading can be used here if a loading indicator is desired.
    const result = await authStore.login(credentialResponse.credential, userLang);
    responseData.value = result; // Store the raw response for debug mode if needed

    // Access user info via authStore.user or authStore.decodedAccessToken if needed.
    // For example: console.log(authStore.user);

    if (!DEBUG_MODE) {
      router.push("/dailydraw"); // Redirect to protected route after successful login
    }
  } catch (err) {
    // The authStore.login action should throw an error, which is caught here.
    // The error might be from the API call or token handling within the store.
    console.error("Login failed in component:", err);
    // Use a more specific error message from the store if available, otherwise use a generic one.
    error.value = err.message || t("login.auth_failed");
  }
};
</script>

<style scoped>
/*
Styles for the login page container.
Specific styles for the Google login button itself should be handled 
within the GoogleLoginButton component's styles or global styles 
that target the underlying vue3-google-login button structure.
*/
.login-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 80vh; /* Adjust as needed */
  padding: 20px;
}

h1 {
  margin-bottom: 20px;
}

/* Add any other specific styles for the LoginPage here */
</style>
