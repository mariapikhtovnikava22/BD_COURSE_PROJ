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
        localStorage.removeItem('role_id');
    },

    get_user_role: () => {
        return localStorage.getItem('role_id');
    },

    // Check if user is admin
    isAdmin: () => {
        return auth.get_user_role() === '1';
    },
};