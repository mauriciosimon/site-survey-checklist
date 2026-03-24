import { useState, useEffect } from 'react';
import api, { API_BASE } from '../api';

export default function FireDoorQuoting() {
  // Existing state
  const [file, setFile] = useState(null);
  const [clientName, setClientName] = useState('');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [surveyType, setSurveyType] = useState('');

  // Rate card state
  const [rateItems, setRateItems] = useState([]);
  const [showAllRates, setShowAllRates] = useState(false);
  const [loadingRates, setLoadingRates] = useState(true);
  const [editingId, setEditingId] = useState(null);
  const [editPrice, setEditPrice] = useState('');

  // Fetch rate card items on mount
  useEffect(() => {
    fetchRateItems();
  }, []);

  const fetchRateItems = async () => {
    try {
      setLoadingRates(true);
      const response = await api.get('/api/firedoor/rates');
      setRateItems(response.data.items || []);
    } catch (err) {
      console.error('Error fetching rate items:', err);
      setRateItems([]); // Set empty array on error
    } finally {
      setLoadingRates(false);
    }
  };

  const handleEditPrice = (item) => {
    setEditingId(item.id);
    setEditPrice(item.unit_price || '');
  };

  const handleSavePrice = async (item) => {
    try {
      await api.put(`/api/firedoor/rates/${item.id}`, {
        unit_price: editPrice
      });
      
      // Update local state
      setRateItems(items => items.map(i => 
        i.id === item.id ? { ...i, unit_price: editPrice } : i
      ));
      
      setEditingId(null);
      setEditPrice('');
    } catch (err) {
      console.error('Error updating price:', err);
      alert('Failed to update price');
    }
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setEditPrice('');
  };

  // Existing handlers
  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      const validTypes = [
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-excel',
        'text/plain'  // Support pre-extracted PDF text files
      ];
      if (!validTypes.includes(selectedFile.type)) {
        setError('Please upload a PDF, Excel, or Text file');
        setFile(null);
        return;
      }
      setFile(selectedFile);
      setError('');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!file) {
      setError('Please select a file');
      return;
    }

    if (!clientName.trim()) {
      setError('Please enter a client name');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');
    setStatus('Processing file...');

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('client_name', clientName);

      const response = await api.post('/api/firedoor/process', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        responseType: 'blob',
      });

      // Read survey type from response headers
      const surveyTypeHeader = response.headers['x-survey-type'] || '';
      setSurveyType(surveyTypeHeader);

      const blob = new Blob([response.data], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      });

      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${clientName.replace(/\s+/g, '_')}_FireDoor_Quote.xlsx`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      setSuccess('Quote generated and downloaded!');
      setStatus('');
      setFile(null);
      setClientName('');
    } catch (err) {
      console.error('Error processing file:', err);
      setError(err.response?.data?.detail || 'Failed to process file');
      setStatus('');
    } finally {
      setLoading(false);
    }
  };

  const displayedRates = showAllRates ? rateItems : rateItems.slice(0, 5);

  return (
    <div className="container">
      <h2>Fire Door Quoting</h2>

      {/* Rate Card Section */}
      <div style={{
        backgroundColor: '#f8f9fa',
        border: '1px solid #dee2e6',
        borderRadius: '8px',
        padding: '20px',
        marginBottom: '25px'
      }}>
        <h3 style={{ marginTop: 0, marginBottom: '15px', fontSize: '18px' }}>
          Current Rate Card Prices
        </h3>

        {loadingRates ? (
          <p style={{ color: '#666' }}>Loading rates...</p>
        ) : (
          <>
            <div style={{ overflowX: 'auto' }}>
              <table style={{
                width: '100%',
                borderCollapse: 'collapse',
                fontSize: '14px'
              }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid #dee2e6', backgroundColor: '#f8f9fa' }}>
                    <th colSpan="2" style={{ padding: '8px', textAlign: 'left', fontWeight: '600', borderRight: '2px solid #dee2e6' }}>
                      BMTrada ART Standard
                    </th>
                    <th colSpan="3" style={{ padding: '8px', textAlign: 'left', fontWeight: '600' }}>
                      WestPark Rate Card
                    </th>
                  </tr>
                  <tr style={{ borderBottom: '2px solid #dee2e6' }}>
                    <th style={{ padding: '8px', textAlign: 'left', fontWeight: '600', width: '80px' }}>ART Code</th>
                    <th style={{ padding: '8px', textAlign: 'left', fontWeight: '600', borderRight: '2px solid #dee2e6' }}>ART Description</th>
                    <th style={{ padding: '8px', textAlign: 'left', fontWeight: '600', width: '80px' }}>B-Code</th>
                    <th style={{ padding: '8px', textAlign: 'left', fontWeight: '600' }}>WestPark Description</th>
                    <th style={{ padding: '8px', textAlign: 'center', fontWeight: '600', width: '120px' }}>Price / Action</th>
                  </tr>
                </thead>
                <tbody>
                  {displayedRates.map((item) => (
                    <tr key={item.id} style={{ borderBottom: '1px solid #dee2e6' }}>
                      <td style={{ padding: '8px', fontWeight: '500' }}>{item.art_code}</td>
                      <td style={{ padding: '8px', borderRight: '2px solid #f0f0f0' }}>
                        {item.description}
                      </td>
                      <td style={{ padding: '8px', fontWeight: '500' }}>{item.rate_card_code}</td>
                      <td style={{ padding: '8px' }}>
                        {item.rate_card_description || '—'}
                      </td>
                      <td style={{ padding: '8px', textAlign: 'center' }}>
                        {editingId === item.id ? (
                          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', alignItems: 'center' }}>
                            <input
                              type="text"
                              value={editPrice}
                              onChange={(e) => setEditPrice(e.target.value)}
                              style={{
                                width: '80px',
                                padding: '4px 8px',
                                border: '1px solid #007bff',
                                borderRadius: '4px',
                                fontSize: '12px'
                              }}
                              autoFocus
                            />
                            <div style={{ display: 'flex', gap: '4px' }}>
                              <button
                                onClick={() => handleSavePrice(item)}
                                style={{
                                  padding: '3px 8px',
                                  fontSize: '11px',
                                  backgroundColor: '#28a745',
                                  color: 'white',
                                  border: 'none',
                                  borderRadius: '3px',
                                  cursor: 'pointer'
                                }}
                              >
                                Save
                              </button>
                              <button
                                onClick={handleCancelEdit}
                                style={{
                                  padding: '3px 8px',
                                  fontSize: '11px',
                                  backgroundColor: '#6c757d',
                                  color: 'white',
                                  border: 'none',
                                  borderRadius: '3px',
                                  cursor: 'pointer'
                                }}
                              >
                                Cancel
                              </button>
                            </div>
                          </div>
                        ) : (
                          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', alignItems: 'center' }}>
                            <span style={{ fontWeight: '500', fontSize: '13px' }}>{item.unit_price || '—'}</span>
                            <button
                              onClick={() => handleEditPrice(item)}
                              style={{
                                padding: '3px 10px',
                                fontSize: '11px',
                                backgroundColor: '#007bff',
                                color: 'white',
                                border: 'none',
                                borderRadius: '3px',
                                cursor: 'pointer'
                              }}
                            >
                              Edit
                            </button>
                          </div>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {rateItems.length > 5 && (
              <button
                onClick={() => setShowAllRates(!showAllRates)}
                style={{
                  marginTop: '15px',
                  padding: '8px 16px',
                  backgroundColor: 'white',
                  border: '1px solid #007bff',
                  color: '#007bff',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontSize: '14px'
                }}
              >
                {showAllRates ? 'Show less' : `See all ${rateItems.length} items`}
              </button>
            )}
          </>
        )}
      </div>

      {/* Compact File Upload Section */}
      <div style={{
        backgroundColor: '#ffffff',
        border: '1px solid #dee2e6',
        borderRadius: '8px',
        padding: '20px'
      }}>
        <h3 style={{ marginTop: 0, marginBottom: '15px', fontSize: '18px' }}>
          Generate Quote
        </h3>

        <form onSubmit={handleSubmit}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', marginBottom: '15px' }}>
            <div>
              <label style={{ display: 'block', marginBottom: '5px', fontSize: '14px', fontWeight: '500' }}>
                Client Name
              </label>
              <input
                type="text"
                value={clientName}
                onChange={(e) => setClientName(e.target.value)}
                placeholder="e.g., Thames Court"
                disabled={loading}
                required
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '1px solid #ced4da',
                  borderRadius: '4px',
                  fontSize: '14px'
                }}
              />
            </div>

            <div>
              <label style={{ display: 'block', marginBottom: '5px', fontSize: '14px', fontWeight: '500' }}>
                Survey File
              </label>
              <input
                type="file"
                onChange={handleFileChange}
                accept=".pdf,.xlsx,.xls,.txt"
                disabled={loading}
                required
                style={{
                  width: '100%',
                  padding: '6px',
                  border: '1px solid #ced4da',
                  borderRadius: '4px',
                  fontSize: '14px'
                }}
              />
            </div>
          </div>

          {loading && (
            <div style={{ padding: '12px', backgroundColor: '#e3f2fd', borderRadius: '4px', marginBottom: '15px' }}>
              <p style={{ margin: 0, color: '#1976d2', fontSize: '14px' }}>{status}</p>
            </div>
          )}

          {error && (
            <div style={{ padding: '12px', backgroundColor: '#ffebee', borderRadius: '4px', marginBottom: '15px' }}>
              <p style={{ margin: 0, color: '#c62828', fontSize: '14px' }}>{error}</p>
            </div>
          )}

          {success && (
            <>
              <div style={{ padding: '12px', backgroundColor: '#e8f5e9', borderRadius: '4px', marginBottom: '15px' }}>
                <p style={{ margin: 0, color: '#2e7d32', fontSize: '14px' }}>{success}</p>
              </div>
              
              {surveyType === 'TYPE_2' && (
                <div style={{ 
                  padding: '12px', 
                  backgroundColor: '#fff3cd', 
                  border: '1px solid #ffc107',
                  borderRadius: '4px', 
                  marginBottom: '15px' 
                }}>
                  <p style={{ margin: 0, color: '#856404', fontSize: '14px', fontWeight: '500' }}>
                    ⚠️ Option B (full replacement) could not be priced — fire strategy drawings were not included in this survey. 
                    To unlock Option B pricing, ask the client for their fire strategy drawings and forward to the estimating team.
                  </p>
                </div>
              )}
            </>
          )}

          <button
            type="submit"
            disabled={loading || !file || !clientName.trim()}
            style={{
              width: '100%',
              padding: '10px',
              backgroundColor: loading || !file || !clientName.trim() ? '#ccc' : '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              fontSize: '16px',
              cursor: loading || !file || !clientName.trim() ? 'not-allowed' : 'pointer'
            }}
          >
            {loading ? 'Processing...' : 'Generate Quote'}
          </button>
        </form>
      </div>
    </div>
  );
}
