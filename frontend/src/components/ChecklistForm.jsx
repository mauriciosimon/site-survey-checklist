import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { checklistApi, API_BASE } from '../api';

const initialFormData = {
  // Header Info
  site_name: '',
  surveyor_name: '',
  survey_date: '',
  site_address: '',
  client_name: '',
  client_contact: '',
  project_name: '',
  // Building Specs
  building_level: '',
  ceiling_height: '',
  skirting_size: '',
  floor_type: '',
  soffit_type: '',
  existing_ceiling_trims: '',
  ceiling_void_depth: '',
  floor_void_depth: '',
  // Access & Logistics
  service_penetrations_scale: '',
  goods_lift_available: false,
  good_staircase_access: false,
  loading_bay_restrictions: '',
  street_restrictions: '',
  noise_restrictions: '',
  // Finishes & Details
  mullion_perimeter_details: '',
  wall_deflection_needed: false,
  door_finish: '',
  frame_type: '',
  glazing_details: '',
  head_track_detail: '',
  // Project Status
  start_date: '',
  project_secured: false,
  programme_available: false,
  // Technical Requirements
  acoustic_baffles_required: false,
  fire_stopping_required: false,
  mullion_details: '',
  // Commercial
  pricing_details: '',
  supplier_notes: '',
  // Documentation
  additional_notes: '',
  site_photos: [],
};

function ChecklistForm() {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEdit = Boolean(id);

  const [formData, setFormData] = useState(initialFormData);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [photoFile, setPhotoFile] = useState(null);

  useEffect(() => {
    if (isEdit) {
      setLoading(true);
      checklistApi.getById(id)
        .then((response) => {
          const data = response.data;
          // Format dates for input fields
          if (data.survey_date) data.survey_date = data.survey_date.split('T')[0];
          if (data.start_date) data.start_date = data.start_date.split('T')[0];
          setFormData({ ...initialFormData, ...data });
        })
        .catch(() => setError('Failed to load checklist'))
        .finally(() => setLoading(false));
    }
  }, [id, isEdit]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.site_name.trim()) {
      setError('Site Name is required');
      return;
    }

    setSaving(true);
    setError(null);

    try {
      // Clean up empty strings to nulls for optional fields
      const cleanData = { ...formData };
      Object.keys(cleanData).forEach((key) => {
        if (cleanData[key] === '') cleanData[key] = null;
      });
      // Convert numeric strings
      if (cleanData.building_level) cleanData.building_level = parseInt(cleanData.building_level);
      if (cleanData.ceiling_height) cleanData.ceiling_height = parseFloat(cleanData.ceiling_height);
      if (cleanData.ceiling_void_depth) cleanData.ceiling_void_depth = parseInt(cleanData.ceiling_void_depth);
      if (cleanData.floor_void_depth) cleanData.floor_void_depth = parseInt(cleanData.floor_void_depth);
      if (cleanData.service_penetrations_scale) cleanData.service_penetrations_scale = parseInt(cleanData.service_penetrations_scale);

      if (isEdit) {
        await checklistApi.update(id, cleanData);
      } else {
        await checklistApi.create(cleanData);
      }
      navigate('/');
    } catch (err) {
      setError('Failed to save checklist. Check your input and try again.');
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  const handlePhotoUpload = async () => {
    if (!photoFile || !id) return;
    try {
      const response = await checklistApi.uploadPhoto(id, photoFile);
      setFormData((prev) => ({ ...prev, site_photos: response.data.site_photos }));
      setPhotoFile(null);
    } catch (err) {
      setError('Failed to upload photo');
    }
  };

  if (loading) return <div className="loading">Loading...</div>;

  return (
    <div className="card">
      <h2>{isEdit ? 'Edit Checklist' : 'New Site Visit Checklist'}</h2>

      {error && <div className="error" style={{ marginTop: '15px' }}>{error}</div>}

      <form onSubmit={handleSubmit}>
        {/* Header Info */}
        <div className="form-section">
          <h3>Header Info</h3>
          <div className="form-grid">
            <div className="form-group">
              <label>Site Name *</label>
              <input
                type="text"
                name="site_name"
                value={formData.site_name}
                onChange={handleChange}
                required
              />
            </div>
            <div className="form-group">
              <label>Surveyor Name</label>
              <input
                type="text"
                name="surveyor_name"
                value={formData.surveyor_name}
                onChange={handleChange}
              />
            </div>
            <div className="form-group">
              <label>Survey Date</label>
              <input
                type="date"
                name="survey_date"
                value={formData.survey_date}
                onChange={handleChange}
              />
            </div>
            <div className="form-group">
              <label>Site Address</label>
              <input
                type="text"
                name="site_address"
                value={formData.site_address}
                onChange={handleChange}
              />
            </div>
            <div className="form-group">
              <label>Client Name</label>
              <input
                type="text"
                name="client_name"
                value={formData.client_name}
                onChange={handleChange}
              />
            </div>
            <div className="form-group">
              <label>Client Contact</label>
              <input
                type="tel"
                name="client_contact"
                value={formData.client_contact}
                onChange={handleChange}
                placeholder="Phone number"
              />
            </div>
            <div className="form-group">
              <label>Project Name</label>
              <input
                type="text"
                name="project_name"
                value={formData.project_name}
                onChange={handleChange}
              />
            </div>
          </div>
        </div>

        {/* Building Specs */}
        <div className="form-section">
          <h3>Building Specs</h3>
          <div className="form-grid">
            <div className="form-group">
              <label>Building Level</label>
              <input
                type="number"
                name="building_level"
                value={formData.building_level}
                onChange={handleChange}
              />
            </div>
            <div className="form-group">
              <label>Ceiling Height (meters)</label>
              <input
                type="number"
                name="ceiling_height"
                value={formData.ceiling_height}
                onChange={handleChange}
                step="0.01"
                min="0"
              />
            </div>
            <div className="form-group">
              <label>Skirting Size</label>
              <select name="skirting_size" value={formData.skirting_size} onChange={handleChange}>
                <option value="">Select...</option>
                <option value="100mm">100mm</option>
                <option value="150mm">150mm</option>
                <option value="200mm">200mm</option>
                <option value="Other">Other</option>
              </select>
            </div>
            <div className="form-group">
              <label>Floor Type</label>
              <select name="floor_type" value={formData.floor_type} onChange={handleChange}>
                <option value="">Select...</option>
                <option value="Raised Floor">Raised Floor</option>
                <option value="Concrete">Concrete</option>
                <option value="Screed">Screed</option>
                <option value="Other">Other</option>
              </select>
            </div>
            <div className="form-group">
              <label>Soffit Type</label>
              <select name="soffit_type" value={formData.soffit_type} onChange={handleChange}>
                <option value="">Select...</option>
                <option value="Rib Deck">Rib Deck</option>
                <option value="Concrete">Concrete</option>
                <option value="Other">Other</option>
              </select>
            </div>
            <div className="form-group">
              <label>Existing Ceiling/Trims</label>
              <input
                type="text"
                name="existing_ceiling_trims"
                value={formData.existing_ceiling_trims}
                onChange={handleChange}
              />
            </div>
            <div className="form-group">
              <label>Ceiling Void Depth (mm)</label>
              <input
                type="number"
                name="ceiling_void_depth"
                value={formData.ceiling_void_depth}
                onChange={handleChange}
                min="0"
              />
            </div>
            <div className="form-group">
              <label>Floor Void Depth (mm)</label>
              <input
                type="number"
                name="floor_void_depth"
                value={formData.floor_void_depth}
                onChange={handleChange}
                min="0"
              />
            </div>
          </div>
        </div>

        {/* Access & Logistics */}
        <div className="form-section">
          <h3>Access & Logistics</h3>
          <div className="form-grid">
            <div className="form-group">
              <label>Service Penetrations Scale (1-10)</label>
              <input
                type="number"
                name="service_penetrations_scale"
                value={formData.service_penetrations_scale}
                onChange={handleChange}
                min="1"
                max="10"
              />
            </div>
            <div className="form-group checkbox-group">
              <input
                type="checkbox"
                name="goods_lift_available"
                checked={formData.goods_lift_available}
                onChange={handleChange}
              />
              <label>Goods Lift Available</label>
            </div>
            <div className="form-group checkbox-group">
              <input
                type="checkbox"
                name="good_staircase_access"
                checked={formData.good_staircase_access}
                onChange={handleChange}
              />
              <label>Good Staircase Access</label>
            </div>
            <div className="form-group">
              <label>Loading Bay Restrictions</label>
              <textarea
                name="loading_bay_restrictions"
                value={formData.loading_bay_restrictions}
                onChange={handleChange}
              />
            </div>
            <div className="form-group">
              <label>Street Restrictions</label>
              <textarea
                name="street_restrictions"
                value={formData.street_restrictions}
                onChange={handleChange}
              />
            </div>
            <div className="form-group">
              <label>Noise Restrictions</label>
              <textarea
                name="noise_restrictions"
                value={formData.noise_restrictions}
                onChange={handleChange}
              />
            </div>
          </div>
        </div>

        {/* Finishes & Details */}
        <div className="form-section">
          <h3>Finishes & Details</h3>
          <div className="form-grid">
            <div className="form-group">
              <label>Mullion/Perimeter Details</label>
              <textarea
                name="mullion_perimeter_details"
                value={formData.mullion_perimeter_details}
                onChange={handleChange}
              />
            </div>
            <div className="form-group checkbox-group">
              <input
                type="checkbox"
                name="wall_deflection_needed"
                checked={formData.wall_deflection_needed}
                onChange={handleChange}
              />
              <label>Wall Deflection Needed</label>
            </div>
            <div className="form-group">
              <label>Door Finish</label>
              <select name="door_finish" value={formData.door_finish} onChange={handleChange}>
                <option value="">Select...</option>
                <option value="Veneer">Veneer</option>
                <option value="PG">PG</option>
                <option value="Laminate">Laminate</option>
                <option value="Paint Grade">Paint Grade</option>
                <option value="Other">Other</option>
              </select>
            </div>
            <div className="form-group">
              <label>Frame Type</label>
              <select name="frame_type" value={formData.frame_type} onChange={handleChange}>
                <option value="">Select...</option>
                <option value="Timber">Timber</option>
                <option value="Metal">Metal</option>
              </select>
            </div>
            <div className="form-group">
              <label>Glazing Details</label>
              <textarea
                name="glazing_details"
                value={formData.glazing_details}
                onChange={handleChange}
              />
            </div>
            <div className="form-group">
              <label>Head Track/Detail</label>
              <textarea
                name="head_track_detail"
                value={formData.head_track_detail}
                onChange={handleChange}
              />
            </div>
          </div>
        </div>

        {/* Project Status */}
        <div className="form-section">
          <h3>Project Status</h3>
          <div className="form-grid">
            <div className="form-group">
              <label>Start Date</label>
              <input
                type="date"
                name="start_date"
                value={formData.start_date}
                onChange={handleChange}
              />
            </div>
            <div className="form-group checkbox-group">
              <input
                type="checkbox"
                name="project_secured"
                checked={formData.project_secured}
                onChange={handleChange}
              />
              <label>Project Secured</label>
            </div>
            <div className="form-group checkbox-group">
              <input
                type="checkbox"
                name="programme_available"
                checked={formData.programme_available}
                onChange={handleChange}
              />
              <label>Programme Available</label>
            </div>
          </div>
        </div>

        {/* Technical Requirements */}
        <div className="form-section">
          <h3>Technical Requirements</h3>
          <div className="form-grid">
            <div className="form-group checkbox-group">
              <input
                type="checkbox"
                name="acoustic_baffles_required"
                checked={formData.acoustic_baffles_required}
                onChange={handleChange}
              />
              <label>Acoustic Baffles Required</label>
            </div>
            <div className="form-group checkbox-group">
              <input
                type="checkbox"
                name="fire_stopping_required"
                checked={formData.fire_stopping_required}
                onChange={handleChange}
              />
              <label>Fire Stopping Required</label>
            </div>
            <div className="form-group" style={{ gridColumn: 'span 2' }}>
              <label>Mullion Details</label>
              <textarea
                name="mullion_details"
                value={formData.mullion_details}
                onChange={handleChange}
                rows={3}
              />
            </div>
          </div>
        </div>

        {/* Commercial */}
        <div className="form-section">
          <h3>Commercial</h3>
          <div className="form-grid">
            <div className="form-group">
              <label>Pricing Details</label>
              <textarea
                name="pricing_details"
                value={formData.pricing_details}
                onChange={handleChange}
              />
            </div>
            <div className="form-group">
              <label>Supplier Notes</label>
              <textarea
                name="supplier_notes"
                value={formData.supplier_notes}
                onChange={handleChange}
              />
            </div>
          </div>
        </div>

        {/* Documentation */}
        <div className="form-section">
          <h3>Documentation</h3>
          <div className="form-group">
            <label>Additional Notes</label>
            <textarea
              name="additional_notes"
              value={formData.additional_notes}
              onChange={handleChange}
              rows={4}
            />
          </div>

          {isEdit && (
            <div className="photo-upload">
              <label>Site Photos</label>
              <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
                <input
                  type="file"
                  accept="image/*"
                  onChange={(e) => setPhotoFile(e.target.files[0])}
                />
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={handlePhotoUpload}
                  disabled={!photoFile}
                >
                  Upload Photo
                </button>
              </div>
              {formData.site_photos && formData.site_photos.length > 0 && (
                <div className="photo-grid">
                  {formData.site_photos.map((photo, idx) => (
                    <img
                      key={idx}
                      src={`${API_BASE}${photo}`}
                      alt={`Site photo ${idx + 1}`}
                    />
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        <div className="form-actions">
          <button type="submit" className="btn btn-success" disabled={saving}>
            {saving ? 'Saving...' : isEdit ? 'Update Checklist' : 'Create Checklist'}
          </button>
          <button type="button" className="btn btn-secondary" onClick={() => navigate('/')}>
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}

export default ChecklistForm;
