<template>
  <div>
    <div ref="googleButtonContainer"></div>
    <!-- custom gomb helyett: -->
    <!-- <button @click="startGoogleLogin">Google Custom Login</button> -->
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, defineEmits } from 'vue'

// Esemény küldése a szülőnek
const emit = defineEmits(['credential-response', 'error'])

// Ref a Google gomb konténeréhez
const googleButtonContainer = ref(null)

// A Google client ID környezeti változóból
const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID

// Felhasználó nyelve
const userLang = navigator.language?.split('-')[0] === 'hu' ? 'hu' : 'en'

// Google SDK betöltése dinamikusan
const loadGoogleScript = () =>
  new Promise((resolve, reject) => {
    if (document.getElementById('google-sdk')) {
      resolve()
      return
    }
    const script = document.createElement('script')
    script.src = 'https://accounts.google.com/gsi/client'
    script.async = true
    script.defer = true
    script.id = 'google-sdk'
    script.onload = resolve
    script.onerror = () => reject(new Error('Google SDK betöltése sikertelen'))
    document.head.appendChild(script)
  })

// A Google bejelentkezés callback-je
const handleCredentialResponse = (response) => {
  if (response.credential) {
    emit('credential-response', response.credential)
  } else {
    emit('error', 'Google bejelentkezés sikertelen')
  }
}

// Google Auth inicializálás és gomb renderelés
const initializeGoogleAuth = () => {
  if (!window.google?.accounts?.id) {
    emit('error', 'Google SDK nem elérhető')
    return
  }
  if (!clientId) {
    emit('error', 'Hiányzó Google client ID')
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
    emit('error', 'Google gomb konténer nem található')
  }
}

onMounted(() => {
  loadGoogleScript()
    .then(initializeGoogleAuth)
    .catch(() => emit('error', 'Google SDK betöltése sikertelen'))
})

onUnmounted(() => {
  if (window.google?.accounts?.id) {
    window.google.accounts.id.cancel()
  }
})
</script>
