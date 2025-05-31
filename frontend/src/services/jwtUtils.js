import * as jwtDecode from "jwt-decode";

/**
 * Decode a JWT token to extract the payload.
 * @param {string} token - JWT token string to decode.
 * @returns {Object|null} - Decoded token payload or null if decoding fails.
 */
export const decodeToken = (token) => {
  try {
    return jwtDecode.jwtDecode(token); // Using jwtDecode.jwtDecode as per import style
  } catch (error) {
    console.error("Failed to decode token:", error);
    return null;
  }
};
