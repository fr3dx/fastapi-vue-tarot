<template>
  <div>
    <h1>Google Bejelentkezés</h1>
    <button id="google-signin-btn">Bejelentkezés Google-val</button>
  </div>
</template>

<script>
export default {
  mounted() {
    const clientId = '928275508669-tf20bv090ega6llrvcp57ct6v74d5me9.apps.googleusercontent.com';

    window.onload = () => {
      google.accounts.id.initialize({
        client_id: clientId,
        callback: this.handleCredentialResponse,  // Itt kezeljük a bejelentkezést
      });

      google.accounts.id.renderButton(
        document.getElementById('google-signin-btn'), 
        { theme: "outline", size: "large" }
      );
    };
  },
  methods: {
    handleCredentialResponse(response) {
      // Ellenőrizzük, hogy sikerült-e bejelentkezni
      if (response && response.credential) {
        console.log("Bejelentkezett, token:", response.credential);
        // Tároljuk el az id_token-t a localStorage-ban
        localStorage.setItem('id_token', response.credential);
        // Irányítjuk a felhasználót a callback oldalra
        this.$router.push({ name: 'Callback' });
      } else {
        console.error("Hiba történt a bejelentkezés során.");
      }
    }
  }
};
</script>
