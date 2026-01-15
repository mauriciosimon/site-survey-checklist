import { BrowserRouter, Routes, Route, Link, useNavigate } from 'react-router-dom';
import ChecklistList from './components/ChecklistList';
import ChecklistForm from './components/ChecklistForm';
import ChecklistDetail from './components/ChecklistDetail';

function Header() {
  const navigate = useNavigate();

  return (
    <header>
      <Link to="/" style={{ color: 'white', textDecoration: 'none' }}>
        <h1>Site Visit Checklists</h1>
      </Link>
      <button className="btn btn-primary" onClick={() => navigate('/new')}>
        + New Checklist
      </button>
    </header>
  );
}

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <Header />
        <Routes>
          <Route path="/" element={<ChecklistList />} />
          <Route path="/new" element={<ChecklistForm />} />
          <Route path="/edit/:id" element={<ChecklistForm />} />
          <Route path="/view/:id" element={<ChecklistDetail />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
