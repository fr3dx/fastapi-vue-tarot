<template>
  <!-- Container for the Google login button -->
  <div class="google-login-button-container">
    <!-- 
      Google OAuth login component from vue3-google-login.
      The 'callback' prop handles the response after a successful login.
      The 'buttonConfig' prop is used to customize the button's appearance.
    -->
    <GoogleLogin 
      :callback="onSuccessCallback" 
      :buttonConfig="buttonConfig" 
    />
  </div>
</template>

<script setup>
import { GoogleLogin } from "vue3-google-login";
import { reactive } from "vue"; // Import reactive for buttonConfig

// Define the props this component accepts.
const props = defineProps({
  onSuccessCallback: {
    type: Function,
    required: true,
  },
});

// Define the button configuration.
// We use reactive because buttonConfig is an object.
const buttonConfig = reactive({
  type: 'icon', // We want to display an icon/image, not a standard button
  size: 'large', // Choose an appropriate size ('small', 'medium', 'large')
  shape: 'rectangular', // Adjust shape if needed ('square', 'circle', 'rectangular', 'pill')
  theme: 'neutral', // Use 'neutral' theme as we are providing our own visual
  text: 'signin_with', // Optional: text to display if needed (though 'icon' type usually doesn't show text)
  locale: navigator.language?.split("-")[0] === "hu" ? "hu" : "en", // Use user's language for button text if visible
});

/**
 * Custom rendering function for the Google Login button.
 * This function replaces the default button provided by vue3-google-login.
 * It returns a Vue VNode or a string containing the HTML for the button.
 * We will render an image tag pointing to our custom SVG.
 */
const buttonConfigRender = (props) => {
  // 'props' here contains properties that vue3-google-login passes,
  // like the onClick handler and the disabled state.
  return h('button', {
    onClick: props.onClick, // Bind the click handler provided by the library
    disabled: props.disabled, // Bind the disabled state
    class: 'custom-google-login-button', // Add a class for custom styling
  }, [
    h('img', {
      src: '/google-login-neutral.svg', // Path to your SVG file in the public directory
      alt: 'Sign in with Google',
      class: 'custom-google-login-icon' // Class for the image if needed
    })
  ]);
};

// We need to provide the render function to the buttonConfig.
// Note: Providing a custom render function overrides most other buttonConfig options
// like type, size, shape, etc., but they might still be useful for internal logic
// of vue3-google-login or for accessibility attributes.
buttonConfig.render = buttonConfigRender;

// Import h from vue if not already imported (implicitly available in Vue 3 setup, but explicit is clearer)
import { h } from 'vue';
</script>

<style scoped>
/* 
Add specific styles for the custom button and icon here.
These styles are scoped to this component.
*/
.google-login-button-container {
  display: flex;
  justify-content: center;
  margin-top: 1rem;
  /* Other container styles */
}

.custom-google-login-button {
  /* Basic button reset for your custom look */
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
  /* Optional: Remove default button focus outline if you provide your own */
  /* outline: none; */
}

.custom-google-login-button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.custom-google-login-icon {
  display: block; /* Ensure the image takes its own line */
  width: 48px; /* Adjust size as needed */
  height: 48px; /* Adjust size as needed */
  /* Optional: Add padding or margin around the icon if desired */
}

/* Optional: Add hover/active states if needed */
.custom-google-login-button:hover .custom-google-login-icon {
  /* Example: Add a slight opacity change on hover */
  opacity: 0.9;
}

/* Ensure the original vue3-google-login styles don't interfere if possible */
/* Depending on how vue3-google-login injects styles, you might need more specific overrides */
</style>
