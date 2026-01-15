import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { adminApi } from '../api';
import { useAuth } from '../AuthContext';

function AdminDashboard() {
  const [users, setUsers] = useState([]);
  const [checklists, setChecklists] = useState([]);
  const [selectedUser, setSelectedUser] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { isAdmin } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAdmin) {
      navigate('/');
      return;
    }
    fetchData();
  }, [isAdmin, navigate]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [usersRes, checklistsRes] = await Promise.all([
        adminApi.getUsers(),
        adminApi.getChecklists(),
      ]);
      setUsers(usersRes.data);
      setChecklists(checklistsRes.data);
      setError(null);
    } catch (err) {
      setError('Failed to load admin data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleUserFilter = async (userId) => {
    setSelectedUser(userId);
    try {
      const response = await adminApi.getChecklists(userId || null);
      setChecklists(response.data);
    } catch (err) {
      setError('Failed to filter checklists');
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString();
  };

  if (loading) {
    return <div className="loading">Loading admin dashboard...</div>;
  }

  return (
    <div>
      <h2 style={{ marginBottom: '20px' }}>Admin Dashboard</h2>

      {error && <div className="error">{error}</div>}

      {/* User Stats */}
      <div className="card" style={{ marginBottom: '20px' }}>
        <h3>Users ({users.length})</h3>
        <table className="checklist-table" style={{ marginTop: '15px' }}>
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Role</th>
              <th>Checklists</th>
              <th>Joined</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id}>
                <td>{user.full_name}</td>
                <td>{user.email}</td>
                <td>
                  <span className={`status-badge ${user.role === 'admin' ? 'status-secured' : 'status-pending'}`}>
                    {user.role}
                  </span>
                </td>
                <td>{user.checklist_count}</td>
                <td>{formatDate(user.created_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* All Checklists */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
          <h3>All Checklists ({checklists.length})</h3>
          <select
            value={selectedUser}
            onChange={(e) => handleUserFilter(e.target.value)}
            style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
          >
            <option value="">All Users</option>
            {users.map((user) => (
              <option key={user.id} value={user.id}>
                {user.full_name} ({user.checklist_count})
              </option>
            ))}
          </select>
        </div>

        {checklists.length === 0 ? (
          <div className="empty-state">No checklists found.</div>
        ) : (
          <table className="checklist-table">
            <thead>
              <tr>
                <th>Site Name</th>
                <th>Owner</th>
                <th>Client</th>
                <th>Survey Date</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {checklists.map((checklist) => (
                <tr key={checklist.id}>
                  <td>
                    <Link to={`/view/${checklist.id}`}>
                      <strong>{checklist.site_name}</strong>
                    </Link>
                  </td>
                  <td>
                    <small>{checklist.owner_name || 'Unknown'}</small>
                    <br />
                    <small style={{ color: '#888' }}>{checklist.owner_email || ''}</small>
                  </td>
                  <td>{checklist.client_name || '-'}</td>
                  <td>{formatDate(checklist.survey_date)}</td>
                  <td>
                    <span className={`status-badge ${checklist.project_secured ? 'status-secured' : 'status-pending'}`}>
                      {checklist.project_secured ? 'Secured' : 'Pending'}
                    </span>
                  </td>
                  <td>
                    <button
                      className="btn btn-secondary"
                      onClick={() => navigate(`/edit/${checklist.id}`)}
                    >
                      Edit
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

export default AdminDashboard;
