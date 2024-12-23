export const auth = {

    // Get token
    getToken: () => {
        return localStorage.getItem('Token');
    },

    // Check if user is logged in
    isAuthenticated: () => {
        return !!localStorage.getItem('Token');
    },

    // Logout
    logout: () => {
        localStorage.removeItem('Token');
    },
};