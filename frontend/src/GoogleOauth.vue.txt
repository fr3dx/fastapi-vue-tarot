<template>
  <div class="p-4">
    <!-- Page title -->
    <h1 class="text-xl font-bold mb-4">{{ t('login.title') }}</h1>

    <!-- Container for the Google sign-in button -->
    <div ref="googleButtonContainer"></div>

    <!-- Error message display -->
    <div v-if="error" class="mt-4 bg-red-100 p-2 rounded">
      <strong>{{ t('login.error_label') }}</strong> {{ error }}
    </div>

    <!-- Debug mode: display raw backend response -->
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

    <!-- Debug mode: display decoded user information -->
    <UserInfo v-if="DEBUG_MODE && decoded" :user="decoded" />
  </div>
</template>

<script setup>
// Vue core + dependencies
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import { jwtDecode } from 'jwt-decode'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

// Localization and routing setup
const { t } = useI18n()
const router = useRouter()

// Debug mode flag from environment
const DEBUG_MODE = import.meta.env.VITE_DEBUG_MODE === 'true'

// Reactive state variables
const idToken = ref(null)
const decoded = ref(null)
const error = ref(null)
const responseData = ref(null)

// Google client ID and DOM ref
const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID
const googleButtonContainer = ref(null)

// Set user language from browser (default to English)
const userLang = navigator.language?.split('-')[0] === 'hu' ? 'hu' : 'en'

/**
 * Handles the response after Google sign-in.
 * Decodes the JWT and sends it to the backend.
 */
const handleCredentialResponse = async (response) => {
  if (response.credential) {
    idToken.value = response.credential

    // Try to decode the JWT token
    try {
      decoded.value = jwtDecode(response.credential)
    } catch (e) {
      error.value = t('login.decode_failed')
      decoded.value = null
      return
    }

    error.value = null
    await sendGoogleAuthRequest(idToken.value, userLang)
  } else {
    error.value = t('login.auth_failed')
    idToken.value = null
    decoded.value = null
  }
}

/**
 * Sends the token and language to the backend for authentication.
 */
const sendGoogleAuthRequest = async (token, lang) => {
  try {
    const res = await axios.post('http://localhost:8000/api/auth/google', { token, lang })
    responseData.value = res.data
    localStorage.setItem('access_token', res.data.access_token)

    // Navigate only if not in debug mode
    if (!DEBUG_MODE) {
      router.push('/dailydraw')
    }
  } catch {
    error.value = t('login.auth_failed')
  }
}

/**
 * Initializes the Google sign-in widget and renders the button.
 */
const initializeGoogleAuth = () => {
  if (!window.google?.accounts?.id) {
    error.value = t('login.script_load_failed')
    return
  }

  if (!clientId) {
    error.value = t('login.missing_client_id')
    return
  }

  window.google.accounts.id.initialize({
    client_id: clientId,
    callback: handleCredentialResponse,
    locale: userLang
  })

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
    error.value = t('login.missing_container')
  }
}

/**
 * Loads Google's OAuth script dynamically.
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

// Load and initialize Google sign-in on mount
onMounted(() => {
  loadGoogleScript()
    .then(initializeGoogleAuth)
    .catch(() => {
      error.value = t('login.script_load_failed')
    })
})

// Cancel the sign-in session when component is destroyed
onUnmounted(() => {
  if (window.google?.accounts?.id) {
    window.google.accounts.id.cancel()
  }
})

/**
 * Component to show decoded user information (debug mode only).
 */
const UserInfo = {
  props: ['user'],
  template: `
    <div class="mt-4 bg-green-100 p-4 rounded">
      <h2 class="font-semibold mb-2">{{ $t('login.decoded_title') }}</h2>
      <ul class="text-sm">
        <li><strong>{{ $t('login.username') }}:</strong> {{ user.name }}</li>
        <li><strong>Email:</strong> {{ user.email }}</li>
        <li><strong>Google ID:</strong> {{ user.sub }}</li>
        <li>
          <strong>{{ $t('login.profile_picture') }}:</strong>
          <img :src="user.picture" alt="profile picture" class="inline w-10 h-10 rounded-full ml-2" />
        </li>
      </ul>
    </div>
  `
}
</script>

<!-- Scoped external style for the component -->
<style src="@/assets/GoogleOauth.css"></style>
