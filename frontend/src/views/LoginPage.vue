<template>
  <div>
    <h2>Google bejelentkezés</h2>
    <GoogleLogin :callback="handleCredentialResponse" />
  </div>
</template>

<script>
import { GoogleLogin } from 'vue3-google-login'
import router from '@/router/router'; // Feltételezve, hogy itt van a routered
import { setAuthToken } from '@/services/authService'; // Ezt a fájlt nemsokára létrehozzuk

export default {
  components: {
    GoogleLogin
  },
  methods: {
    async handleCredentialResponse(response) {
      console.log("Encoded JWT ID token: " + response.credential);
      // Itt küldjük el az ID tokent a FastAPI backendnek
      try {
        const backendUrl = 'http://localhost:8000/api/auth/google'; // Cseréld ki a backend URL-re
        const res = await fetch(backendUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ token: response.credential, lang: 'hu' }) // Nyelv beállítása, ha szükséges
        });

        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }

        const data = await res.json();
        console.log("Received JWT token from backend:", data.access_token);

        // Tároljuk a JWT tokent (pl. Local Storage-ben)
        setAuthToken(data.access_token);

        // Átirányítás védett oldalra
        router.push('/dailydraw'); // Cseréld ki a kívánt oldalra

      } catch (error) {
        console.error("Error during Google login with backend:", error);
        // Hibakezelés: pl. hibaüzenet megjelenítése a felhasználónak
      }
    }
  }
}
</script>
