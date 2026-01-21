import { useState, useEffect, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { checklistApi } from '../api';
import { useWorkspace } from '../WorkspaceContext';

function ChecklistList() {
  const { currentWorkspace } = useWorkspace();
  const [checklists, setChecklists] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const fetchChecklists = useCallback(async () => {
    try {
      setLoading(true);
      const response = await checklistApi.getAll({
        search,
        workspace_id: currentWorkspace?.id,
      });
      setChecklists(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load checklists. Make sure the backend is running.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [search, currentWorkspace]);

  useEffect(() => {
    if (currentWorkspace) {
      fetchChecklists();
    }
  }, [fetchChecklists, currentWorkspace]);

  const handleSearch = (e) => {
    e.preventDefault();
    fetchChecklists();
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this checklist?')) return;
    try {
      await checklistApi.delete(id);
      fetchChecklists();
    } catch (err) {
      setError('Failed to delete checklist');
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString();
  };

  if (loading) {
    return <div className="loading">Loading checklists...</div>;
  }

  return (
    <div>
      {error && <div className="error">{error}</div>}

      <form className="search-bar" onSubmit={handleSearch}>
        <input
          type="text"
          placeholder="Search by site name, client, project..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <button type="submit" className="btn btn-primary">Search</button>
      </form>

      <div className="card">
        {checklists.length === 0 ? (
          <div className="empty-state">
            <p>No checklists found.</p>
            <button
              className="btn btn-primary"
              style={{ marginTop: '15px' }}
              onClick={() => navigate('/new')}
            >
              Create your first checklist
            </button>
          </div>
        ) : (
          <table className="checklist-table">
            <thead>
              <tr>
                <th>Site Name</th>
                <th>Surveyor</th>
                <th>Client</th>
                <th>Project</th>
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
                  <td>{checklist.surveyor_name || '-'}</td>
                  <td>{checklist.client_name || '-'}</td>
                  <td>{checklist.project_name || '-'}</td>
                  <td>{formatDate(checklist.survey_date)}</td>
                  <td>
                    <span className={`status-badge ${checklist.project_secured ? 'status-secured' : 'status-pending'}`}>
                      {checklist.project_secured ? 'Secured' : 'Pending'}
                    </span>
                  </td>
                  <td className="actions">
                    <button
                      className="btn btn-secondary"
                      onClick={() => navigate(`/edit/${checklist.id}`)}
                    >
                      Edit
                    </button>
                    <button
                      className="btn btn-danger"
                      onClick={() => handleDelete(checklist.id)}
                    >
                      Delete
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

export default ChecklistList;
