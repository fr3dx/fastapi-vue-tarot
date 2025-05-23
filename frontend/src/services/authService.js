// services/authService.js

export const TOKEN_KEY = 'jwtToken'; // Exportáld a TOKEN_KEY-t is!

export const setAuthToken = (token) => {
  if (token) {
    localStorage.setItem(TOKEN_KEY, token);
  } else {
    localStorage.removeItem(TOKEN_KEY);
  }
};

export const getAuthToken = () => {
  return localStorage.getItem(TOKEN_KEY);
};

export const isAuthenticated = () => {
  const token = getAuthToken();
  return !!token;
};
