import { BrowserRouter, Routes, Route, Link, useNavigate, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './AuthContext';
import ChecklistList from './components/ChecklistList';
import ChecklistForm from './components/ChecklistForm';
import ChecklistDetail from './components/ChecklistDetail';
import Login from './components/Login';
import Register from './components/Register';
import AdminDashboard from './components/AdminDashboard';

// Protected Route Component
function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

function Header() {
  const navigate = useNavigate();
  const { user, logout, isAdmin } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header>
      <Link to="/" style={{ color: 'white', textDecoration: 'none' }} className="logo-section">
        <img src="/logo.png" alt="West Park Contracting" className="logo" />
        <h1>Site Survey Checklists</h1>
      </Link>
      <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
        {user ? (
          <>
            {isAdmin && (
              <button className="btn btn-secondary" onClick={() => navigate('/admin')}>
                Admin
              </button>
            )}
            <button className="btn btn-primary" onClick={() => navigate('/new')}>
              + New Checklist
            </button>
            <div className="user-menu">
              <span style={{ color: 'white', marginRight: '10px' }}>
                {user.full_name}
                {isAdmin && <span style={{ marginLeft: '5px', fontSize: '12px', opacity: 0.8 }}>(Admin)</span>}
              </span>
              <button className="btn btn-secondary" onClick={handleLogout}>
                Logout
              </button>
            </div>
          </>
        ) : (
          <>
            <button className="btn btn-secondary" onClick={() => navigate('/login')}>
              Sign In
            </button>
            <button className="btn btn-primary" onClick={() => navigate('/register')}>
              Sign Up
            </button>
          </>
        )}
      </div>
    </header>
  );
}

function AppContent() {
  const { loading } = useAuth();

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="app">
      <Header />
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Protected routes */}
        <Route path="/" element={
          <ProtectedRoute>
            <ChecklistList />
          </ProtectedRoute>
        } />
        <Route path="/new" element={
          <ProtectedRoute>
            <ChecklistForm />
          </ProtectedRoute>
        } />
        <Route path="/edit/:id" element={
          <ProtectedRoute>
            <ChecklistForm />
          </ProtectedRoute>
        } />
        <Route path="/view/:id" element={
          <ProtectedRoute>
            <ChecklistDetail />
          </ProtectedRoute>
        } />
        <Route path="/admin" element={
          <ProtectedRoute>
            <AdminDashboard />
          </ProtectedRoute>
        } />
      </Routes>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
