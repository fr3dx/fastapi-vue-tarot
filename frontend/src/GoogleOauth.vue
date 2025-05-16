<template>
  <div class="p-4">
    <h1 class="text-xl font-bold mb-4">Google Login</h1>

    <!-- Google Login Button Container -->
    <div ref="googleButtonContainer"></div>

    <!-- Error message displayed to the user -->
    <div v-if="error" class="mt-4 bg-red-100 p-2 rounded">
      <strong>Hiba történt:</strong> {{ error }}
    </div>

    <!-- Backend response shown only in debug mode -->
    <div v-if="DEBUG_MODE && responseData" class="mt-4 bg-blue-100 p-4 rounded">
      <h2 class="font-semibold mb-2">Backend válasz:</h2>
      <ul class="text-sm">
        <li><strong>Access Token:</strong> {{ responseData.access_token }}</li>
        <li><strong>Token Type:</strong> {{ responseData.token_type }}</li>
        <li v-if="responseData.username"><strong>Felhasználónév:</strong> {{ responseData.username }}</li>
      </ul>
      <p class="mt-2 text-sm text-gray-700">Ez a backend által kiállított hozzáférési token és kapcsolódó adatok.</p>
    </div>

    <!-- Decoded user information shown only in debug mode -->
    <UserInfo v-if="DEBUG_MODE && decoded" :user="decoded" />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import { jwtDecode } from 'jwt-decode'
import { useRouter } from 'vue-router'

// Enable debug mode based on environment variable
const DEBUG_MODE = import.meta.env.VITE_DEBUG_MODE === 'true'

const router = useRouter()

// Reactive state variables
const idToken = ref(null)          // Stores raw JWT from Google
const decoded = ref(null)          // Stores decoded user info from JWT
const error = ref(null)            // Stores error message for user feedback
const responseData = ref(null)     // Stores backend response data
const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID // Google OAuth client ID from env
const googleButtonContainer = ref(null) // Reference to Google sign-in button container

/**
 * Handles Google credential response after login
 * @param {Object} response - The response object from Google OAuth
 */
const handleCredentialResponse = async (response) => {
  if (response.credential) {
    idToken.value = response.credential

    try {
      // Decode JWT to extract user info
      decoded.value = jwtDecode(response.credential)
    } catch (e) {
      error.value = 'Felhasználói adatok dekódolása sikertelen.'
      decoded.value = null
      return
    }

    error.value = null

    // Send token to backend for verification and further auth
    await sendGoogleAuthRequest(idToken.value)
  } else {
    error.value = 'Google bejelentkezési hiba történt.'
    idToken.value = null
    decoded.value = null
  }
}

/**
 * Sends the Google ID token to the backend for authentication
 * @param {string} token - The ID token (JWT) from Google
 */
const sendGoogleAuthRequest = async (token) => {
  try {
    const res = await axios.post('http://localhost:8000/api/auth/google', { token })
    responseData.value = res.data

    // Store access token locally for further authenticated requests
    localStorage.setItem('access_token', res.data.access_token)

    // Redirect user if not in debug mode
    if (!DEBUG_MODE) {
      router.push('/dialydraw')
    }
  } catch {
    error.value = 'Backend hitelesítési hiba.'
  }
}

/**
 * Initializes Google OAuth client and renders the sign-in button
 */
const initializeGoogleAuth = () => {
  if (!window.google?.accounts?.id) {
    error.value = 'Google OAuth szkript nem töltődött be. Ellenőrizd az internetkapcsolatot!'
    return
  }

  if (!clientId) {
    error.value = 'A Google kliens azonosító nincs beállítva.'
    return
  }

  // Initialize Google Identity Services
  window.google.accounts.id.initialize({
    client_id: clientId,
    callback: handleCredentialResponse
  })

  // Render the Google Sign-In button
  if (googleButtonContainer.value) {
    window.google.accounts.id.renderButton(googleButtonContainer.value, {
      type: 'standard',
      shape: 'rectangular',
      theme: 'outline',
      text: 'sign_in_with',
      size: 'large',
      logo_alignment: 'left'
    })
  } else {
    error.value = 'Bejelentkezés gomb konténer nem található.'
  }
}

/**
 * Loads the Google OAuth client script dynamically
 * @returns {Promise<void>}
 */
const loadGoogleScript = () =>
  new Promise((resolve, reject) => {
    const script = document.createElement('script')
    script.src = 'https://accounts.google.com/gsi/client'
    script.async = true
    script.defer = true
    script.onload = resolve
    script.onerror = reject
    document.head.appendChild(script)
  })

// Lifecycle hook: on component mount
onMounted(() => {
  loadGoogleScript()
    .then(initializeGoogleAuth)
    .catch(() => {
      error.value = 'Nem sikerült betölteni a Google OAuth szkriptet.'
    })
})

// Lifecycle hook: on component unmount
onUnmounted(() => {
  if (window.google?.accounts?.id) {
    window.google.accounts.id.cancel()
  }
})

/**
 * Inline component to display decoded user information (for debugging)
 */
const UserInfo = {
  props: ['user'],
  template: `
    <div class="mt-4 bg-green-100 p-4 rounded">
      <h2 class="font-semibold mb-2">Dekódolt felhasználói adatok:</h2>
      <ul class="text-sm">
        <li><strong>Felhasználónév:</strong> {{ user.name }}</li>
        <li><strong>Email:</strong> {{ user.email }}</li>
        <li><strong>Google ID:</strong> {{ user.sub }}</li>
        <li>
          <strong>Profilkép:</strong>
          <img :src="user.picture" alt="profile picture" class="inline w-10 h-10 rounded-full ml-2" />
        </li>
      </ul>
    </div>
  `
}
</script>

<style src="@/assets/GoogleOauth.css"></style>
