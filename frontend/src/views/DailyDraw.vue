<script setup>
// Vue and libraries
import { ref, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import axios from 'axios';
import '@/assets/DailyDraw.css';
import { isAuthenticated as checkAuthServiceAuthenticated, TOKEN_KEY } from '@/services/authService';


// Localization instance

const isAuthenticated = ref(checkAuthServiceAuthenticated());
const { t, locale } = useI18n();

// Reactive state variables
const card = ref(null);            // Stores drawn card details
const errorMessage = ref(null);    // Stores error messages for user feedback
const loading = ref(false);        // Loading state for async calls
const description = ref(null);     // Card description text
//const isAuthenticated = ref(false); // User authentication status

// Retrieve token from localStorage using the imported TOKEN_KEY
const getToken = () => localStorage.getItem(TOKEN_KEY);

// Backend URL from environment variables
const backendUrl = import.meta.env.VITE_BACKEND_URL;

/**
 * Checks if user is authenticated based on presence of JWT token.
 * Use the imported isAuthenticated from authService for consistency
 */
const checkAuthentication = () => {
  isAuthenticated.value = checkAuthServiceAuthenticated();
};

// Run authentication check when component mounts
onMounted(() => {
  checkAuthentication();
});

/**
 * Draw a daily card from the backend API.
 * Includes JWT token in Authorization header.
 */
const drawCard = async () => {
  if (loading.value) return; // Prevent multiple simultaneous requests
  loading.value = true;
  description.value = null; // Reset description on new draw
  errorMessage.value = null;

  try {
    const token = getToken();
    const response = await axios.get(`${backendUrl}/api/daily_card`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    card.value = response.data;

    // Fetch localized card name
    const res = await fetch(`${backendUrl}/api/card_description/${card.value.key}?lang=${locale.value}`);
    if (res.ok) {
      const data = await res.json();
      card.value.name = data.name ?? card.value.name;
    }
  } catch (e) {
    console.error('Draw error:', e);
    card.value = null;

    if (e.response?.status === 403) {
      errorMessage.value = t('dailyDraw.error_already_drawn');
    } else {
      errorMessage.value = t('dailyDraw.error_general');
    }
  } finally {
    loading.value = false;
  }
};

/**
 * Reveal and fetch localized description of the drawn card.
 */
const revealDescription = async () => {
  if (!card.value?.key) return;

  try {
    const res = await fetch(`${backendUrl}/api/card_description/${card.value.key}?lang=${locale.value}`);
    if (!res.ok) throw new Error('Description fetch failed');

    const data = await res.json();
    card.value.name = data.name ?? card.value.name;
    description.value = data.description;
  } catch (e) {
    console.error('Description error:', e);
    description.value = t('dailyDraw.description_error');
  }
};
    console.log('Script setup end - isAuthenticated.value:', isAuthenticated.value);
</script>
