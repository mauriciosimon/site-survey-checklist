import { BrowserRouter, Routes, Route, Link, useNavigate, Navigate, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './AuthContext';
import Sidebar from './components/Sidebar';
import ChecklistList from './components/ChecklistList';
import ChecklistForm from './components/ChecklistForm';
import ChecklistDetail from './components/ChecklistDetail';
import Login from './components/Login';
import Register from './components/Register';
import AdminDashboard from './components/AdminDashboard';
import LeadsPage from './components/LeadsPage';
import DealsPage from './components/DealsPage';
import AccountsPage from './components/AccountsPage';
import ContactsPage from './components/ContactsPage';
import TasksPage from './components/TasksPage';
import {
  DashboardPage,
  ProjectsPage
} from './components/PlaceholderPage';

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

// Layout with sidebar for authenticated users
function MainLayout({ children }) {
  const { user } = useAuth();
  const location = useLocation();

  // Don't show sidebar on auth pages
  const isAuthPage = ['/login', '/register'].includes(location.pathname);

  if (!user || isAuthPage) {
    return <div className="main-content-full">{children}</div>;
  }

  return (
    <div className="app-layout">
      <Sidebar />
      <main className="main-content">
        {children}
      </main>
    </div>
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
      <MainLayout>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Dashboard */}
          <Route path="/" element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          } />

          {/* Sales routes */}
          <Route path="/leads" element={
            <ProtectedRoute>
              <LeadsPage />
            </ProtectedRoute>
          } />
          <Route path="/deals" element={
            <ProtectedRoute>
              <DealsPage />
            </ProtectedRoute>
          } />
          <Route path="/tasks" element={
            <ProtectedRoute>
              <TasksPage />
            </ProtectedRoute>
          } />

          {/* Clients routes */}
          <Route path="/accounts" element={
            <ProtectedRoute>
              <AccountsPage />
            </ProtectedRoute>
          } />
          <Route path="/contacts" element={
            <ProtectedRoute>
              <ContactsPage />
            </ProtectedRoute>
          } />

          {/* Projects routes */}
          <Route path="/projects" element={
            <ProtectedRoute>
              <ProjectsPage />
            </ProtectedRoute>
          } />

          {/* Site Checklists routes */}
          <Route path="/checklists" element={
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

          {/* Admin routes */}
          <Route path="/admin" element={
            <ProtectedRoute>
              <AdminDashboard />
            </ProtectedRoute>
          } />
        </Routes>
      </MainLayout>
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
