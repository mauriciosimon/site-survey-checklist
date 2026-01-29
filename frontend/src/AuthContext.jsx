import { createContext, useContext, useState, useEffect } from 'react';
import { authApi } from './api';

const AuthContext = createContext(null);

// Demo credentials for sharing
const DEMO_EMAIL = 'demo@killmonday.app';
const DEMO_PASSWORD = 'demo123';

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      // Check for demo mode via URL parameter
      const urlParams = new URLSearchParams(window.location.search);
      if (urlParams.get('demo') === 'admin') {
        // Clean URL first
        window.history.replaceState({}, '', window.location.pathname);
        
        try {
          // Try to login with demo credentials
          const response = await authApi.login({ email: DEMO_EMAIL, password: DEMO_PASSWORD });
          const { access_token, user: demoUser } = response.data;
          localStorage.setItem('token', access_token);
          localStorage.setItem('user', JSON.stringify(demoUser));
          setUser(demoUser);
        } catch (err) {
          // If login fails, try to register
          try {
            const response = await authApi.register({ 
              email: DEMO_EMAIL, 
              password: DEMO_PASSWORD,
              full_name: 'Demo Admin'
            });
            const { access_token, user: demoUser } = response.data;
            localStorage.setItem('token', access_token);
            localStorage.setItem('user', JSON.stringify(demoUser));
            setUser(demoUser);
          } catch (regErr) {
            console.error('Demo login failed:', regErr);
          }
        }
        setLoading(false);
        return;
      }

      // Check for existing token on mount
      const token = localStorage.getItem('token');
      const savedUser = localStorage.getItem('user');

      if (token && savedUser) {
        setUser(JSON.parse(savedUser));
        
        // Verify token is still valid
        try {
          const response = await authApi.me();
          setUser(response.data);
          localStorage.setItem('user', JSON.stringify(response.data));
        } catch (err) {
          // Token invalid - clear auth
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          setUser(null);
        }
      }
      setLoading(false);
    };

    initAuth();
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
