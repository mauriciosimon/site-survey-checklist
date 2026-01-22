import { useState, createContext, useContext, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Link, useNavigate, Navigate, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './AuthContext';
import { WorkspaceProvider } from './WorkspaceContext';
import { Search, Bell, Settings, LogOut, Menu, X } from 'lucide-react';

// Mobile sidebar context
const MobileSidebarContext = createContext();
export const useMobileSidebar = () => useContext(MobileSidebarContext);
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
import OpportunitiesPage from './components/OpportunitiesPage';
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
  const [showUserMenu, setShowUserMenu] = useState(false);
  const { mobileOpen, setMobileOpen } = useMobileSidebar();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // Get user initials
  const getInitials = (name) => {
    if (!name) return 'U';
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  };

  return (
    <header>
      <div className="header-left">
        {user && (
          <button
            className="mobile-menu-btn"
            onClick={() => setMobileOpen(!mobileOpen)}
            aria-label="Toggle menu"
          >
            {mobileOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        )}
        <Link to="/" className="logo-section">
          <img src="/logo.png" alt="West Park Contracting" className="logo" />
        </Link>
        {user && (
          <div className="header-search">
            <Search size={16} className="search-icon" />
            <input type="text" placeholder="Search..." />
          </div>
        )}
      </div>

      <div className="header-right">
        {user ? (
          <>
            <button className="header-icon-btn" title="Notifications">
              <Bell size={20} />
            </button>
            {isAdmin && (
              <button className="header-icon-btn" onClick={() => navigate('/admin')} title="Admin Settings">
                <Settings size={20} />
              </button>
            )}
            <div className="user-menu-container">
              <button
                className="user-avatar"
                onClick={() => setShowUserMenu(!showUserMenu)}
                title={user.full_name}
              >
                {getInitials(user.full_name)}
              </button>
              {showUserMenu && (
                <div className="user-dropdown">
                  <div className="user-dropdown-header">
                    <div className="user-avatar-large">{getInitials(user.full_name)}</div>
                    <div className="user-info">
                      <span className="user-name">{user.full_name}</span>
                      <span className="user-email">{user.email}</span>
                    </div>
                  </div>
                  <div className="user-dropdown-divider" />
                  <button className="user-dropdown-item" onClick={handleLogout}>
                    <LogOut size={16} />
                    <span>Logout</span>
                  </button>
                </div>
              )}
            </div>
          </>
        ) : (
          <>
            <button className="btn btn-ghost" onClick={() => navigate('/login')}>
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
  const { mobileOpen, setMobileOpen } = useMobileSidebar();

  // Don't show sidebar on auth pages
  const isAuthPage = ['/login', '/register'].includes(location.pathname);

  if (!user || isAuthPage) {
    return <div className="main-content-full">{children}</div>;
  }

  return (
    <div className="app-layout">
      {/* Mobile overlay */}
      {mobileOpen && (
        <div
          className="mobile-overlay"
          onClick={() => setMobileOpen(false)}
        />
      )}
      <Sidebar mobileOpen={mobileOpen} onCloseMobile={() => setMobileOpen(false)} />
      <main className="main-content">
        {children}
      </main>
    </div>
  );
}

function AppContent() {
  const { loading } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();

  // Close mobile sidebar on navigation
  useEffect(() => {
    setMobileOpen(false);
  }, [location.pathname]);

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <MobileSidebarContext.Provider value={{ mobileOpen, setMobileOpen }}>
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
          <Route path="/opportunities" element={
            <ProtectedRoute>
              <OpportunitiesPage />
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
    </MobileSidebarContext.Provider>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <WorkspaceProvider>
          <AppContent />
        </WorkspaceProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
