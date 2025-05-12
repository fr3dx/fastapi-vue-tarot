<template>
  <div class="p-4">
    <h1 class="text-xl font-bold mb-4">Google OAuth Test</h1>

    <!-- Google Login Button Container -->
    <div ref="googleButtonContainer"></div>

    <!-- Error Message -->
    <div v-if="error" class="mt-4 bg-red-100 p-2 rounded">
      <strong>Error occurred: </strong> {{ error }}
    </div>

    <!-- Display ID Token & Decoded Information -->
    <div v-if="idToken" class="mt-4 bg-gray-100 p-2 rounded">
      <h2 class="font-semibold mb-2">ID Token (Raw):</h2>
      <p class="break-words text-sm">{{ idToken }}</p>
    </div>

    <!-- Display backend response -->
    <div v-if="responseData" class="mt-4 bg-blue-100 p-4 rounded">
      <h2 class="font-semibold mb-2">Backend Response:</h2>
      <ul class="text-sm">
        <li><strong>Access Token:</strong> {{ responseData.access_token }}</li>
        <li><strong>Token Type:</strong> {{ responseData.token_type }}</li>
      </ul>
    </div>

    <div v-if="decoded" class="mt-4 bg-green-100 p-4 rounded">
      <h2 class="font-semibold mb-2">Decoded User Data:</h2>
      <ul class="text-sm">
        <li><strong>User Name:</strong> {{ decoded.name }}</li>
        <li><strong>Email:</strong> {{ decoded.email }}</li>
        <li><strong>Google ID:</strong> {{ decoded.sub }}</li>
        <li>
          <strong>Picture:</strong>
          <img
            :src="decoded.picture"
            alt="profile picture"
            class="inline w-10 h-10 rounded-full ml-2"
          />
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import axios from 'axios'; // Import axios
import { jwtDecode } from 'jwt-decode'; // JWT decoding
import { useRouter } from 'vue-router'; // Importing the router for navigation

const router = useRouter(); // Accessing the router
const idToken = ref(null);
const decoded = ref(null);
const error = ref(null);
const responseData = ref(null); // Storing the backend response
const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID; // Environment variable for client ID

const googleButtonContainer = ref(null);

// Handling Google OAuth response
const handleCredentialResponse = async (response) => {
  if (response.credential) {
    idToken.value = response.credential;
    try {
      decoded.value = jwtDecode(response.credential); // Decoding the ID token
    } catch (e) {
      console.error('Hiba a JWT dekódolás során:', e);
      error.value = 'Hiba történt a felhasználói adatok dekódolásakor.';
      decoded.value = null;
      return;
    }

    error.value = null;
    await sendGoogleAuthRequest(idToken.value);  // Sending Google token to the backend
  } else {
    error.value = 'Hiba történt a Google bejelentkezés során.';
    idToken.value = null;
    decoded.value = null;
    console.error('Hiba a Google bejelentkezés során:', response);
  }
};

// Sending Google authentication token to the backend
const sendGoogleAuthRequest = async (token) => {
  try {
    const response = await axios.post('http://localhost:8000/api/auth/google', {
      token: token,  // Backend expects the token
    });

    console.log('Backend válasz:', response.data);  // Logging backend response
    localStorage.setItem('access_token', response.data.access_token);

    // Storing the response data on the frontend
    responseData.value = response.data;

    // Redirecting the user to /dialydraw page after successful authentication
    // router.push('/dialydraw'); // Redirect happens here
  } catch (error) {
    console.error('Hiba a backend hitelesítés során:', error);
    error.value = 'Hiba történt a bejelentkezés során (backend)';
  }
};

// Initializing Google OAuth
const initializeGoogleAuth = () => {
  if (!window.google || !window.google.accounts) {
    error.value = 'A Google OAuth script nem töltődött be. Ellenőrizd az internetkapcsolatot és próbáld újra.';
    return;
  }

  if (!clientId) {
    error.value = 'A Google kliensazonosító nincs konfigurálva. Ellenőrizd a .env fájlt.';
    console.error('Kliensazonosító hiányzik. Kérlek, állítsd be a VITE_GOOGLE_CLIENT_ID környezeti változót.');
    return;
  }

  window.google.accounts.id.initialize({
    client_id: clientId,
    callback: handleCredentialResponse,
  });

  if (googleButtonContainer.value) {
    window.google.accounts.id.renderButton(googleButtonContainer.value, {
      type: 'standard',
      shape: 'rectangular',
      theme: 'outline',
      text: 'sign_in_with',
      size: 'large',
      logo_alignment: 'left',
    });
  } else {
    console.error('Nem található a gomb konténer elem.');
    error.value = 'Hiba történt a bejelentkezési gomb betöltésekor.';
  }
};

// Loading Google OAuth script
const loadGoogleScript = () => {
  return new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.defer = true;
    script.onload = resolve;
    script.onerror = reject;
    document.head.appendChild(script);
  });
};

onMounted(() => {
  loadGoogleScript()
    .then(() => {
      initializeGoogleAuth();
    })
    .catch((err) => {
      console.error('Hiba a Google OAuth script betöltése közben:', err);
      error.value = 'Hiba történt a Google OAuth script betöltése közben.';
    });
});

onUnmounted(() => {
  if (window.google && window.google.accounts && window.google.accounts.id) {
    window.google.accounts.id.cancel(); // Recommended cleanup when the component is destroyed
  }
});
</script>
