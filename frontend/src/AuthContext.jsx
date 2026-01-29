import { createContext, useContext, useState, useEffect } from 'react';
import { authApi } from './api';

const AuthContext = createContext(null);

// Demo admin user for sharing
const DEMO_ADMIN = {
  id: 'demo-admin',
  email: 'admin@killmonday.app',
  full_name: 'Demo Admin',
  role: 'admin'
};
const DEMO_TOKEN = 'demo-admin-token-killmonday';

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for demo mode via URL parameter
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('demo') === 'admin') {
      // Auto-login as demo admin
      localStorage.setItem('token', DEMO_TOKEN);
      localStorage.setItem('user', JSON.stringify(DEMO_ADMIN));
      setUser(DEMO_ADMIN);
      setLoading(false);
      // Clean URL
      window.history.replaceState({}, '', window.location.pathname);
      return;
    }

    // Check for existing token on mount
    const token = localStorage.getItem('token');
    const savedUser = localStorage.getItem('user');

    if (token && savedUser) {
      setUser(JSON.parse(savedUser));
      // Verify token is still valid
      authApi.me()
        .then(response => {
          setUser(response.data);
          localStorage.setItem('user', JSON.stringify(response.data));
        })
        .catch(() => {
          logout();
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email, password) => {
    const response = await authApi.login({ email, password });
    const { access_token, user } = response.data;
    localStorage.setItem('token', access_token);
    localStorage.setItem('user', JSON.stringify(user));
    setUser(user);
    return user;
  };

  const register = async (email, password, fullName) => {
    const response = await authApi.register({
      email,
      password,
      full_name: fullName,
    });
    const { access_token, user } = response.data;
    localStorage.setItem('token', access_token);
    localStorage.setItem('user', JSON.stringify(user));
    setUser(user);
    return user;
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  };

  const isAdmin = user?.role === 'admin';

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading, isAdmin }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
