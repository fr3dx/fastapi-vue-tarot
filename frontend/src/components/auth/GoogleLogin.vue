<template>
  <div>
    <!-- Container for rendering the Google Sign-In button -->
    <div ref="googleButtonContainer"></div>

    <!-- Uncomment for custom login button fallback -->
    <!-- <button @click="startGoogleLogin">Google Custom Login</button> -->
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, defineEmits } from "vue";

// Emit events to parent component (for credential or error feedback)
const emit = defineEmits(["credential-response", "error"]);

// Reference to the DOM element where the Google button will be rendered
const googleButtonContainer = ref(null);

// Google OAuth client ID from environment variables
const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;

// Detect user's language (default to 'en' if not Hungarian)
const userLang = navigator.language?.split("-")[0] === "hu" ? "hu" : "en";

// Dynamically load the Google Identity Services SDK
const loadGoogleScript = () =>
  new Promise((resolve, reject) => {
    if (document.getElementById("google-sdk")) {
      resolve();
      return;
    }
    const script = document.createElement("script");
    script.src = "https://accounts.google.com/gsi/client";
    script.async = true;
    script.defer = true;
    script.id = "google-sdk";
    script.onload = resolve;
    script.onerror = () => reject(new Error("Failed to load Google SDK"));
    document.head.appendChild(script);
  });

// Handle the Google Sign-In credential response
const handleCredentialResponse = (response) => {
  if (response.credential) {
    emit("credential-response", response.credential);
  } else {
    emit("error", "Google login failed");
  }
};

// Initialize the Google Sign-In client and render the button
const initializeGoogleAuth = () => {
  if (!window.google?.accounts?.id) {
    emit("error", "Google SDK is not available");
    return;
  }
  if (!clientId) {
    emit("error", "Missing Google client ID");
    return;
  }

  window.google.accounts.id.initialize({
    client_id: clientId,
    callback: handleCredentialResponse,
    locale: userLang,
  });

  if (googleButtonContainer.value) {
    window.google.accounts.id.renderButton(googleButtonContainer.value, {
      type: "standard",
      shape: "rectangular",
      theme: "outline",
      text: "sign_in_with",
      size: "large",
      logo_alignment: "left",
    });
  } else {
    emit("error", "Google button container not found");
  }
};

// Load and initialize Google Sign-In on mount
onMounted(() => {
  loadGoogleScript()
    .then(initializeGoogleAuth)
    .catch(() => emit("error", "Failed to load Google SDK"));
});

// Clean up Google Sign-In session on component unmount
onUnmounted(() => {
  if (window.google?.accounts?.id) {
    window.google.accounts.id.cancel();
  }
});
</script>
