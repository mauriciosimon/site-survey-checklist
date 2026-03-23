import { useState } from 'react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function FireDoorQuoting() {
  const [file, setFile] = useState(null);
  const [clientName, setClientName] = useState('');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      // Validate file type
      const validTypes = [
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-excel'
      ];
      if (!validTypes.includes(selectedFile.type)) {
        setError('Please upload a PDF or Excel file');
        setFile(null);
        return;
      }
      setFile(selectedFile);
      setError('');
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      const validTypes = [
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-excel'
      ];
      if (!validTypes.includes(droppedFile.type)) {
        setError('Please upload a PDF or Excel file');
        return;
      }
      setFile(droppedFile);
      setError('');
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
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
    setStatus('Uploading file...');

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('client_name', clientName);

      setStatus('Processing file...');

      const response = await axios.post(`${API_URL}/api/firedoor/process`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        responseType: 'blob', // Important for file download
      });

      setStatus('Generating Excel quote...');

      // Create blob from response
      const blob = new Blob([response.data], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      });

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${clientName.replace(/\s+/g, '_')}_FireDoor_Quote_${new Date().toISOString().split('T')[0]}.xlsx`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      setSuccess('Quote generated successfully! File downloaded.');
      setStatus('');
      setFile(null);
      setClientName('');
    } catch (err) {
      console.error('Error processing file:', err);
      setError(err.response?.data?.detail || 'Failed to process file. Please try again.');
      setStatus('');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h2>Fire Door Quoting</h2>
      <p style={{ marginBottom: '20px', color: '#666' }}>
        Upload a fire door survey (PDF or Excel) to generate a quote with mapped rate card codes.
      </p>

      <form onSubmit={handleSubmit} className="checklist-form">
        {/* Client Name Input */}
        <div className="form-group">
          <label htmlFor="clientName">Client Name *</label>
          <input
            type="text"
            id="clientName"
            value={clientName}
            onChange={(e) => setClientName(e.target.value)}
            placeholder="e.g., Alpha Sights - Thames Court"
            disabled={loading}
            required
          />
        </div>

        {/* File Upload Drop Zone */}
        <div className="form-group">
          <label>Upload Fire Door Survey *</label>
          <div
            className="file-upload-zone"
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            style={{
              border: '2px dashed #ccc',
              borderRadius: '8px',
              padding: '30px',
              textAlign: 'center',
              backgroundColor: file ? '#f0f9ff' : '#fafafa',
              cursor: 'pointer',
              transition: 'all 0.3s ease'
            }}
          >
            <input
              type="file"
              onChange={handleFileChange}
              accept=".pdf,.xlsx,.xls"
              style={{ display: 'none' }}
              id="file-input"
              disabled={loading}
            />
            <label
              htmlFor="file-input"
              style={{ cursor: loading ? 'not-allowed' : 'pointer', display: 'block' }}
            >
              {file ? (
                <div>
                  <p style={{ fontSize: '16px', fontWeight: 'bold', color: '#0066cc' }}>
                    📄 {file.name}
                  </p>
                  <p style={{ fontSize: '14px', color: '#666', marginTop: '8px' }}>
                    Click to change file
                  </p>
                </div>
              ) : (
                <div>
                  <p style={{ fontSize: '16px', marginBottom: '8px' }}>
                    Drop file here or click to browse
                  </p>
                  <p style={{ fontSize: '14px', color: '#666' }}>
                    Supported: PDF, Excel (.xlsx, .xls)
                  </p>
                </div>
              )}
            </label>
          </div>
        </div>

        {/* Status Messages */}
        {loading && (
          <div style={{
            padding: '15px',
            backgroundColor: '#e3f2fd',
            border: '1px solid #2196f3',
            borderRadius: '4px',
            marginBottom: '15px'
          }}>
            <p style={{ margin: 0, color: '#1976d2' }}>{status}</p>
          </div>
        )}

        {error && (
          <div style={{
            padding: '15px',
            backgroundColor: '#ffebee',
            border: '1px solid #f44336',
            borderRadius: '4px',
            marginBottom: '15px'
          }}>
            <p style={{ margin: 0, color: '#c62828' }}>❌ {error}</p>
          </div>
        )}

        {success && (
          <div style={{
            padding: '15px',
            backgroundColor: '#e8f5e9',
            border: '1px solid #4caf50',
            borderRadius: '4px',
            marginBottom: '15px'
          }}>
            <p style={{ margin: 0, color: '#2e7d32' }}>✅ {success}</p>
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          className="btn btn-primary"
          disabled={loading || !file || !clientName.trim()}
          style={{
            width: '100%',
            padding: '12px',
            fontSize: '16px',
            opacity: (loading || !file || !clientName.trim()) ? 0.6 : 1
          }}
        >
          {loading ? 'Processing...' : 'Generate Quote'}
        </button>
      </form>

      {/* Help Text */}
      <div style={{
        marginTop: '30px',
        padding: '20px',
        backgroundColor: '#f5f5f5',
        borderRadius: '8px'
      }}>
        <h3 style={{ marginTop: 0 }}>How it works:</h3>
        <ol style={{ paddingLeft: '20px', lineHeight: '1.8' }}>
          <li>Upload a fire door survey file (PDF or Excel)</li>
          <li>System detects format and extracts door data</li>
          <li>Maps ART codes to WestPark rate card codes</li>
          <li>Generates populated Excel quote for download</li>
        </ol>
        <p style={{ marginBottom: 0, fontSize: '14px', color: '#666' }}>
          <strong>Supported formats:</strong> FireDNA/RiskBase PDFs with ART codes, Excel surveys with fault columns
        </p>
      </div>
    </div>
  );
}
