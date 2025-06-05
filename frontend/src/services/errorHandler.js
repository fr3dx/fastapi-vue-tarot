import router from '@/router/router';

/**
 * General API error handler. Determines the appropriate action and
 * returns a localized error message based on the incoming error status code.
 *
 * @param {Object} error - The Axios error object from the failed request.
 * @param {Function} t - The i18n translation function for localized messages.
 * @param {Object} authStore - The authentication store instance for managing user state.
 * @returns {String} - A localized error message to display to the user.
 */
export async function handleApiError(error, t, authStore) {
  // Handle network errors or cases with no response (e.g., server unreachable)
  if (!error.response) {
    return t('errors.network_error') || 'Network error, please try again.';
  }

  const status = error.response.status;

  // Handle unauthorized access: logout user and redirect to login page
  if (status === 401) {
    authStore.logout();
    await router.push('/login');
    return t('errors.unauthorized');
  }

  // Handle other HTTP error statuses with appropriate localized messages
  switch (status) {
    case 400:
      return t('errors.bad_request');
    case 403:
      return t('errors.forbidden');
    case 404:
      return t('errors.not_found');
    case 429:
      return t('errors.too_many_requests');
    case 500:
      return t('errors.server_error');
    default:
      // Use server-provided message if available; otherwise return generic error
      return error.response.data?.message || t('errors.general');
  }
}
