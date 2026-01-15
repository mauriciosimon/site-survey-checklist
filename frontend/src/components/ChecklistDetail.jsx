import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { checklistApi, API_BASE } from '../api';

function ChecklistDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [checklist, setChecklist] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchChecklist = async () => {
      try {
        const response = await checklistApi.getById(id);
        setChecklist(response.data);
      } catch (err) {
        setError('Failed to load checklist');
      } finally {
        setLoading(false);
      }
    };
    fetchChecklist();
  }, [id]);

  const formatDate = (dateStr) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString();
  };

  const renderField = (label, value) => {
    if (typeof value === 'boolean') {
      return (
        <div className="detail-field">
          <span className="detail-label">{label}:</span>
          <span className="detail-value">{value ? 'Yes' : 'No'}</span>
        </div>
      );
    }
    return (
      <div className="detail-field">
        <span className="detail-label">{label}:</span>
        <span className="detail-value">{value || '-'}</span>
      </div>
    );
  };

  if (loading) return <div className="loading">Loading...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!checklist) return <div className="error">Checklist not found</div>;

  return (
    <div>
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2>{checklist.site_name}</h2>
          <div style={{ display: 'flex', gap: '10px' }}>
            <button className="btn btn-primary" onClick={() => navigate(`/edit/${id}`)}>
              Edit
            </button>
            <button className="btn btn-secondary" onClick={() => navigate('/')}>
              Back to List
            </button>
          </div>
        </div>

        <style>{`
          .detail-section { margin-bottom: 25px; }
          .detail-section h3 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 8px; margin-bottom: 15px; }
          .detail-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 10px; }
          .detail-field { padding: 8px 0; }
          .detail-label { font-weight: 600; color: #555; margin-right: 8px; }
          .detail-value { color: #333; }
        `}</style>

        <div className="detail-section">
          <h3>Header Info</h3>
          <div className="detail-grid">
            {renderField('Site Name', checklist.site_name)}
            {renderField('Surveyor Name', checklist.surveyor_name)}
            {renderField('Survey Date', formatDate(checklist.survey_date))}
            {renderField('Site Address', checklist.site_address)}
            {renderField('Client Name', checklist.client_name)}
            {renderField('Client Contact', checklist.client_contact)}
            {renderField('Project Name', checklist.project_name)}
          </div>
        </div>

        <div className="detail-section">
          <h3>Building Specs</h3>
          <div className="detail-grid">
            {renderField('Building Level', checklist.building_level)}
            {renderField('Ceiling Height', checklist.ceiling_height ? `${checklist.ceiling_height}m` : null)}
            {renderField('Skirting Size', checklist.skirting_size)}
            {renderField('Floor Type', checklist.floor_type)}
            {renderField('Soffit Type', checklist.soffit_type)}
            {renderField('Existing Ceiling/Trims', checklist.existing_ceiling_trims)}
            {renderField('Ceiling Void Depth', checklist.ceiling_void_depth ? `${checklist.ceiling_void_depth}mm` : null)}
            {renderField('Floor Void Depth', checklist.floor_void_depth ? `${checklist.floor_void_depth}mm` : null)}
          </div>
        </div>

        <div className="detail-section">
          <h3>Access & Logistics</h3>
          <div className="detail-grid">
            {renderField('Service Penetrations Scale', checklist.service_penetrations_scale ? `${checklist.service_penetrations_scale}/10` : null)}
            {renderField('Goods Lift Available', checklist.goods_lift_available)}
            {renderField('Good Staircase Access', checklist.good_staircase_access)}
            {renderField('Loading Bay Restrictions', checklist.loading_bay_restrictions)}
            {renderField('Street Restrictions', checklist.street_restrictions)}
            {renderField('Noise Restrictions', checklist.noise_restrictions)}
          </div>
        </div>

        <div className="detail-section">
          <h3>Finishes & Details</h3>
          <div className="detail-grid">
            {renderField('Mullion/Perimeter Details', checklist.mullion_perimeter_details)}
            {renderField('Wall Deflection Needed', checklist.wall_deflection_needed)}
            {renderField('Door Finish', checklist.door_finish)}
            {renderField('Frame Type', checklist.frame_type)}
            {renderField('Glazing Details', checklist.glazing_details)}
            {renderField('Head Track/Detail', checklist.head_track_detail)}
          </div>
        </div>

        <div className="detail-section">
          <h3>Project Status</h3>
          <div className="detail-grid">
            {renderField('Start Date', formatDate(checklist.start_date))}
            {renderField('Project Secured', checklist.project_secured)}
            {renderField('Programme Available', checklist.programme_available)}
          </div>
        </div>

        <div className="detail-section">
          <h3>Technical Requirements</h3>
          <div className="detail-grid">
            {renderField('Acoustic Baffles Required', checklist.acoustic_baffles_required)}
            {renderField('Fire Stopping Required', checklist.fire_stopping_required)}
            {renderField('Mullion Details', checklist.mullion_details)}
          </div>
        </div>

        <div className="detail-section">
          <h3>Commercial</h3>
          <div className="detail-grid">
            {renderField('Pricing Details', checklist.pricing_details)}
            {renderField('Supplier Notes', checklist.supplier_notes)}
          </div>
        </div>

        <div className="detail-section">
          <h3>Documentation</h3>
          {renderField('Additional Notes', checklist.additional_notes)}
          {checklist.site_photos && checklist.site_photos.length > 0 && (
            <div style={{ marginTop: '15px' }}>
              <strong>Site Photos:</strong>
              <div className="photo-grid">
                {checklist.site_photos.map((photo, idx) => (
                  <img
                    key={idx}
                    src={`${API_BASE}${photo}`}
                    alt={`Site photo ${idx + 1}`}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ChecklistDetail;
