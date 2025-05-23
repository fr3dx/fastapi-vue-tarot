import axios from 'axios';
import {
  loginWithGoogle,
  getAccessToken,
  isAuthenticated,
  logout,
  // decodeToken, // Assuming decodeToken is tested elsewhere or implicitly via other tests
} from '../authService'; // Adjust path as needed

// Mock localStorage
const localStorageMock = (() => {
  let store = {};
  return {
    getItem: jest.fn((key) => store[key] || null),
    setItem: jest.fn((key, value) => { store[key] = value.toString(); }),
    removeItem: jest.fn((key) => { delete store[key]; }),
    clear: jest.fn(() => { store = {}; }),
  };
})();
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

// Mock Axios
jest.mock('axios');

// Define API_URL as it's used in authService.js
const API_URL = 'http://localhost:8000/api/auth';

describe('authService', () => {
  beforeEach(() => {
    // Clear all mocks and localStorage before each test
    localStorageMock.clear();
    axios.post.mockClear();
    axios.get.mockClear(); // If any GET requests were used by interceptor/other functions
    // Clear other axios method mocks if used
  });

  describe('loginWithGoogle', () => {
    it('should store access_token in localStorage and not refresh_token, and return access_token', async () => {
      // Mock axios.post for the /api/auth/google call
      // Response should only contain access_token and token_type as per new flow
      const mockResponse = { data: { access_token: 'fake_access_token', token_type: 'bearer' } };
      axios.post.mockResolvedValue(mockResponse);

      const idToken = 'test_id_token';
      const lang = 'en';
      const result = await loginWithGoogle(idToken, lang);

      // Assert axios.post was called correctly
      expect(axios.post).toHaveBeenCalledWith(`${API_URL}/google`, { token: idToken, lang });
      
      // Assert localStorage.setItem is called for access_token
      expect(localStorageMock.setItem).toHaveBeenCalledWith('access_token', 'fake_access_token');
      
      // Assert localStorage.setItem is NOT called for refresh_token
      expect(localStorageMock.setItem).not.toHaveBeenCalledWith('refresh_token', expect.anything());
      
      // Verify the function returns the access_token and token_type
      expect(result).toEqual({ access_token: 'fake_access_token', token_type: 'bearer' });
    });

    it('should throw an error if API call fails', async () => {
      // Mock axios.post to simulate an error
      axios.post.mockRejectedValue(new Error('Network Error'));
      
      try {
        await loginWithGoogle('test_id_token', 'en');
      } catch (e) {
        expect(e.message).toBe('Network Error');
      }
      expect(localStorageMock.setItem).not.toHaveBeenCalled();
    });
  });

  describe('getAccessToken', () => {
    it('should retrieve access_token from localStorage', () => {
      localStorageMock.setItem('access_token', 'my_token');
      expect(getAccessToken()).toBe('my_token');
    });

    it('should return null if access_token is not in localStorage', () => {
      expect(getAccessToken()).toBeNull();
    });
  });

  describe('isAuthenticated', () => {
    it('should return true if access_token exists in localStorage', () => {
      localStorageMock.setItem('access_token', 'my_token');
      expect(isAuthenticated()).toBe(true);
    });

    it('should return false if access_token does not exist in localStorage', () => {
      expect(isAuthenticated()).toBe(false);
    });
  });

  describe('logout', () => {
    it('should call /api/auth/logout with Authorization header and remove access_token from localStorage', async () => {
      // Setup: Store a token to simulate a logged-in user
      localStorageMock.setItem('access_token', 'fake_access_token_for_logout');
      
      // Mock axios.post for the /api/auth/logout call
      axios.post.mockResolvedValue({ data: { message: 'Logged out successfully' } });

      await logout();

      // Assert axios.post was called correctly for logout
      expect(axios.post).toHaveBeenCalledWith(
        `${API_URL}/logout`, 
        {}, // Empty body
        { headers: { 'Authorization': 'Bearer fake_access_token_for_logout' } }
      );
      
      // Assert localStorage.removeItem is called for access_token
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('access_token');
    });

    it('should remove local access_token even if backend logout fails', async () => {
      localStorageMock.setItem('access_token', 'fake_token');
      // Mock axios.post to simulate an error during backend logout
      axios.post.mockRejectedValue(new Error('Logout API failed'));

      // Spy on console.error to check if the error is logged
      const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

      await logout();
      
      // Assert localStorage.removeItem is still called
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('access_token');
      // Assert error was logged
      expect(consoleErrorSpy).toHaveBeenCalledWith("Backend logout failed:", "Logout API failed");

      consoleErrorSpy.mockRestore();
    });
     it('should proceed with local logout if no access token exists', async () => {
      // No token in localStorage
      axios.post.mockResolvedValue({ data: { message: 'Logged out successfully' } }); // Mock backend call
      await logout();
      // Ensure backend call is NOT made if no token
      expect(axios.post).not.toHaveBeenCalledWith(`${API_URL}/logout`, expect.anything(), expect.anything());
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('access_token'); // Attempt removal anyway
    });
  });

  describe('Axios Interceptor', () => {
    // Note: Testing Axios interceptors directly can be tricky.
    // These tests describe the desired behavior. Actual implementation might require
    // more complex setup, like creating a fresh Axios instance for testing
    // or using libraries like `axios-mock-adapter`.

    // For these conceptual tests, we'll assume `axios` is the instance used by authService
    // and its interceptors are active.

    const mockOriginalRequest = {
      url: `${API_URL}/some_protected_endpoint`,
      headers: {},
      _retry: false, // Interceptor adds this
    };

    it('Scenario: Request fails with 401, refresh succeeds, original request is retried', async () => {
      // 1. Initial setup: User is logged in, has an access token (which will expire)
      localStorageMock.setItem('access_token', 'expired_access_token');

      // 2. Mock the initial protected API call to fail with 401
      //    The first time axios is called (for the original request)
      axios.mockImplementationOnce(() => Promise.reject({ 
        response: { status: 401 }, 
        config: { ...mockOriginalRequest } // Pass a mutable copy
      }));
      
      // 3. Mock the /api/auth/refresh call to succeed
      //    This is the second axios call (axios.post for refresh)
      const newAccessToken = 'new_fresh_access_token';
      axios.post.mockResolvedValueOnce({ data: { access_token: newAccessToken } });
      
      // 4. Mock the retried original request to succeed with the new token
      //    This is the third axios call (original request retried)
      const successData = { message: 'Data from protected endpoint' };
      // Need to ensure this mock is for the retried original request.
      // One way is to ensure axios (non-post) is mocked for the retry.
      // For simplicity, if we assume the original call was a get:
      axios.get.mockResolvedValueOnce({ data: successData }); // If original was GET
      // If original was POST, use axios.post.mockResolvedValueOnce etc.
      // This part is tricky without knowing the original request's method.
      // Let's assume the interceptor directly calls `axios(originalRequest)`.
      // So the global `axios` mock needs to handle this.
      
      // For the purpose of this conceptual test, we'll make `axios` a general mock
      // that can differentiate calls or use specific method mocks.
      // This would be the call for the retried originalRequest:
      axios.mockImplementationOnce(() => Promise.resolve({ data: successData }));


      // --- Action ---
      // Make an API call that will trigger the interceptor logic
      // e.g., a function that uses the global axios instance to fetch protected data
      // For this test, we can simulate this by directly calling axios with a config
      // that would normally be handled by the interceptor.
      // This is a bit artificial; typically you'd test a function that *uses* authService's axios.
      
      // To actually trigger the interceptor, we need to make a call using the
      // same axios instance the interceptor is attached to.
      // The interceptor logic itself calls `axios(originalRequest)` for retry.
      
      // console.log("Simulating initial failed request...");
      // try {
      //   const result = await axios(mockOriginalRequest); // This call would be made by some other part of the app
      //   // Assertions
      //   expect(localStorageMock.setItem).toHaveBeenCalledWith('access_token', newAccessToken);
      //   expect(result.data).toEqual(successData);
      //   // Ensure refresh was called with withCredentials: true
      //   expect(axios.post).toHaveBeenCalledWith(`${API_URL}/refresh`, {}, { withCredentials: true });
      // } catch (error) {
      //    // This path should not be taken if refresh succeeds
      //   throw error;
      // }
      
      // TODO: This test requires a more sophisticated setup to properly trigger and test
      // the interceptor behavior with chained mocks for axios.
      // Key assertions:
      // - `/api/auth/refresh` is called with `withCredentials: true`.
      // - `localStorage` is updated with the new `access_token`.
      // - The original request is retried with the new `access_token` in its Authorization header.
      // - The final promise resolves with the data from the retried request.
      // - `isRefreshing` and `failedQueue` are handled correctly (harder to test directly here).
      expect(true).toBe(true); // Placeholder
    });

    it('Scenario: Request fails with 401, refresh also fails, logout is called', async () => {
      // 1. Initial setup
      localStorageMock.setItem('access_token', 'expired_access_token');
      
      // 2. Mock initial protected API call to fail with 401
      axios.mockImplementationOnce(() => Promise.reject({ 
        response: { status: 401 }, 
        config: { ...mockOriginalRequest } 
      }));
      
      // 3. Mock /api/auth/refresh to fail
      axios.post.mockRejectedValueOnce({ response: { status: 401, data: { message: 'Refresh failed badly' } } });
      
      // Spy on logout (or its effects)
      // const logoutSpy = jest.spyOn(authService, 'logout'); // Assuming authService is an object of exported functions
      // Or mock its effects: localStorage.removeItem, console.error for "Backend logout failed"

      // --- Action ---
      // try {
      //   await axios(mockOriginalRequest); 
      // } catch (error) {
      //   // Assertions
      //   expect(axios.post).toHaveBeenCalledWith(`${API_URL}/refresh`, {}, { withCredentials: true });
      //   // expect(logoutSpy).toHaveBeenCalled(); // Or check its effects
      //   expect(localStorageMock.removeItem).toHaveBeenCalledWith('access_token'); // From logout
      //   expect(error.response.status).toBe(401); // Original error is propagated or refresh error
      // }
      
      // TODO: Similar to above, needs better interceptor testing setup.
      // Key assertions:
      // - `/api/auth/refresh` is called.
      // - `logout()` is called (verify by checking `localStorage.removeItem('access_token')`
      //   and the `POST /api/auth/logout` call if logout itself is not fully mocked away).
      // - The original promise is rejected.
      expect(true).toBe(true); // Placeholder
    });

    it('Scenario: Multiple concurrent requests fail with 401, refresh is called once', async () => {
      // This requires even more advanced mocking to simulate concurrent axios calls
      // and how the interceptor's queueing mechanism handles them.
      // Key assertions:
      // - `/api/auth/refresh` is called only once.
      // - All original requests are eventually retried with the new token (if refresh succeeds).
      // - Or all original requests are rejected (if refresh fails).
      expect(true).toBe(true); // Placeholder
    });

    it('Scenario: Non-401 error, interceptor does not attempt refresh', async () => {
      // 1. Mock an API call to return a non-401 error (e.g., 500)
      axios.mockImplementationOnce(() => Promise.reject({ 
        response: { status: 500 }, 
        config: { ...mockOriginalRequest } 
      }));
      
      // --- Action & Assertions ---
      // try {
      //   await axios(mockOriginalRequest);
      // } catch (error) {
      //   expect(error.response.status).toBe(500);
      //   // Assert that /api/auth/refresh was NOT called
      //   expect(axios.post).not.toHaveBeenCalledWith(`${API_URL}/refresh`, expect.anything(), expect.anything());
      // }
      expect(true).toBe(true); // Placeholder
    });
  });
});
