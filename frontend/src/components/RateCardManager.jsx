import { useState, useEffect } from 'react';
import { API_URL } from '../api';

function RateCardManager() {
  const [rates, setRates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [editValues, setEditValues] = useState({});
  const [seeding, setSeeding] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    loadRates();
  }, [searchTerm]);

  const loadRates = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      const url = searchTerm
        ? `${API_URL}/firedoor/rates?search=${encodeURIComponent(searchTerm)}`
        : `${API_URL}/firedoor/rates`;
      
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to load rates');
      }

      const data = await response.json();
      setRates(data.items || []);
    } catch (error) {
      console.error('Error loading rates:', error);
      setMessage({ type: 'error', text: 'Failed to load rate card items' });
    } finally {
      setLoading(false);
    }
  };

  const handleSeedDatabase = async () => {
    if (!confirm('This will load rate card items from the CSV file. Continue?')) {
      return;
    }

    try {
      setSeeding(true);
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_URL}/firedoor/rates/seed`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to seed database');
      }

      const data = await response.json();
      setMessage({ type: 'success', text: data.message });
      loadRates();
    } catch (error) {
      console.error('Error seeding database:', error);
      setMessage({ type: 'error', text: error.message });
    } finally {
      setSeeding(false);
    }
  };

  const startEditing = (item) => {
    setEditingId(item.id);
    setEditValues({
      unit_price: item.unit_price || '',
      category: item.category || ''
    });
  };

  const cancelEditing = () => {
    setEditingId(null);
    setEditValues({});
  };

  const saveEdit = async (itemId) => {
    try {
      setSaving(true);
      const token = localStorage.getItem('access_token');
      
      const formData = new FormData();
      formData.append('unit_price', editValues.unit_price || '');
      formData.append('category', editValues.category || '');

      const response = await fetch(`${API_URL}/firedoor/rates/${itemId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      if (!response.ok) {
        throw new Error('Failed to update rate');
      }

      const updatedItem = await response.json();
      
      // Update local state
      setRates(rates.map(item => 
        item.id === itemId ? updatedItem : item
      ));
      
      setMessage({ type: 'success', text: 'Rate updated successfully' });
      setEditingId(null);
      setEditValues({});
    } catch (error) {
      console.error('Error saving rate:', error);
      setMessage({ type: 'error', text: 'Failed to save changes' });
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="container" style={{ maxWidth: '1200px', margin: '20px auto' }}>
      <div style={{ marginBottom: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>Rate Card Management</h2>
        <button
          className="btn btn-primary"
          onClick={handleSeedDatabase}
          disabled={seeding || rates.length > 0}
        >
          {seeding ? 'Loading...' : 'Seed from CSV'}
        </button>
      </div>

      {message && (
        <div
          style={{
            padding: '10px 15px',
            marginBottom: '15px',
            borderRadius: '4px',
            backgroundColor: message.type === 'success' ? '#d4edda' : '#f8d7da',
            color: message.type === 'success' ? '#155724' : '#721c24',
            border: `1px solid ${message.type === 'success' ? '#c3e6cb' : '#f5c6cb'}`
          }}
        >
          {message.text}
          <button
            onClick={() => setMessage(null)}
            style={{
              float: 'right',
              background: 'none',
              border: 'none',
              fontSize: '20px',
              cursor: 'pointer',
              color: 'inherit'
            }}
          >
            ×
          </button>
        </div>
      )}

      <div style={{ marginBottom: '20px' }}>
        <input
          type="text"
          placeholder="Search by ART code, description, or rate card code..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{
            width: '100%',
            padding: '10px',
            fontSize: '14px',
            border: '1px solid #ddd',
            borderRadius: '4px'
          }}
        />
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <p>Loading rate card...</p>
        </div>
      ) : rates.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '40px', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
          <p>No rate card items found.</p>
          <p style={{ marginTop: '10px', fontSize: '14px', color: '#666' }}>
            Click "Seed from CSV" to load the initial rate card data.
          </p>
        </div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
            <thead>
              <tr style={{ backgroundColor: '#f8f9fa', borderBottom: '2px solid #dee2e6' }}>
                <th style={{ padding: '12px', textAlign: 'left', width: '10%' }}>ART Code</th>
                <th style={{ padding: '12px', textAlign: 'left', width: '35%' }}>Description</th>
                <th style={{ padding: '12px', textAlign: 'left', width: '12%' }}>Rate Card</th>
                <th style={{ padding: '12px', textAlign: 'left', width: '12%' }}>Unit Price</th>
                <th style={{ padding: '12px', textAlign: 'left', width: '15%' }}>Category</th>
                <th style={{ padding: '12px', textAlign: 'center', width: '16%' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {rates.map((item) => (
                <tr key={item.id} style={{ borderBottom: '1px solid #dee2e6' }}>
                  <td style={{ padding: '10px', fontWeight: '500' }}>{item.art_code}</td>
                  <td style={{ padding: '10px', fontSize: '13px' }}>{item.description}</td>
                  <td style={{ padding: '10px' }}>{item.rate_card_code}</td>
                  <td style={{ padding: '10px' }}>
                    {editingId === item.id ? (
                      <input
                        type="text"
                        value={editValues.unit_price}
                        onChange={(e) => setEditValues({ ...editValues, unit_price: e.target.value })}
                        placeholder="£0.00"
                        style={{
                          width: '100%',
                          padding: '5px',
                          border: '1px solid #ced4da',
                          borderRadius: '3px'
                        }}
                      />
                    ) : (
                      <span>{item.unit_price || '—'}</span>
                    )}
                  </td>
                  <td style={{ padding: '10px' }}>
                    {editingId === item.id ? (
                      <input
                        type="text"
                        value={editValues.category}
                        onChange={(e) => setEditValues({ ...editValues, category: e.target.value })}
                        placeholder="Category"
                        style={{
                          width: '100%',
                          padding: '5px',
                          border: '1px solid #ced4da',
                          borderRadius: '3px'
                        }}
                      />
                    ) : (
                      <span>{item.category || '—'}</span>
                    )}
                  </td>
                  <td style={{ padding: '10px', textAlign: 'center' }}>
                    {editingId === item.id ? (
                      <div style={{ display: 'flex', gap: '5px', justifyContent: 'center' }}>
                        <button
                          onClick={() => saveEdit(item.id)}
                          disabled={saving}
                          className="btn btn-primary"
                          style={{ padding: '5px 10px', fontSize: '12px' }}
                        >
                          {saving ? 'Saving...' : 'Save'}
                        </button>
                        <button
                          onClick={cancelEditing}
                          disabled={saving}
                          className="btn btn-secondary"
                          style={{ padding: '5px 10px', fontSize: '12px' }}
                        >
                          Cancel
                        </button>
                      </div>
                    ) : (
                      <button
                        onClick={() => startEditing(item)}
                        className="btn btn-secondary"
                        style={{ padding: '5px 15px', fontSize: '12px' }}
                      >
                        Edit
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <div style={{ marginTop: '15px', fontSize: '13px', color: '#666' }}>
            Showing {rates.length} item{rates.length !== 1 ? 's' : ''}
          </div>
        </div>
      )}
    </div>
  );
}

export default RateCardManager;
