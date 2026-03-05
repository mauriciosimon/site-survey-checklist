import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { checklistApi, API_BASE } from '../api';
import { useAuth } from '../AuthContext';

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
  goods_lift_notes: '',
  good_staircase_access: false,
  staircase_access_notes: '',
  loading_bay_restrictions: '',
  street_restrictions: '',
  noise_restrictions: '',
  // Finishes & Details
  mullion_perimeter_details: '',
  wall_deflection_needed: false,
  wall_deflection_notes: '',
  door_finish: '',
  door_finish_other: '',
  frame_type: '',
  frame_type_other: '',
  glazing_details: '',
  head_track_detail: '',
  // Project Status
  start_date: '',
  project_secured: false,
  programme_available: false,
  // Technical Requirements
  acoustic_baffles_required: false,
  acoustic_baffles_notes: '',
  fire_stopping_required: false,
  fire_stopping_notes: '',
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
  const { user } = useAuth();
  const isEdit = Boolean(id);

  const [formData, setFormData] = useState(initialFormData);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [photoFile, setPhotoFile] = useState(null);
  const [pendingPhotos, setPendingPhotos] = useState([]); // Photos to upload on create
  const [draftSaved, setDraftSaved] = useState(false);
  const [draftId, setDraftId] = useState(null); // Track backend draft ID for auto-save

  // Auto-save draft to BACKEND (Gmail-style, debounced)
  useEffect(() => {
    // Skip if editing an existing non-draft survey
    if (isEdit && !formData.is_draft) return;
    
    const timeoutId = setTimeout(async () => {
      // Don't save if form is essentially empty
      if (!formData.site_name && !formData.client_name && !formData.site_address) {
        return;
      }

      try {
        // Prepare data for backend
        const cleanData = { ...formData, is_draft: true };
        Object.keys(cleanData).forEach((key) => {
          if (cleanData[key] === '') cleanData[key] = null;
        });

        if (draftId || id) {
          // Update existing draft
          await checklistApi.update(draftId || id, cleanData);
          console.log('[AUTO-SAVE] Draft updated:', draftId || id);
        } else {
          // Create new draft
          const response = await checklistApi.create(cleanData);
          setDraftId(response.data.id);
          console.log('[AUTO-SAVE] Draft created:', response.data.id);
        }

        setDraftSaved(true);
        setTimeout(() => setDraftSaved(false), 2000);
      } catch (err) {
        console.error('[AUTO-SAVE] Failed:', err);
      }
    }, 3000); // 3 second debounce to avoid hammering API

    return () => clearTimeout(timeoutId);
  }, [formData, isEdit, draftId, id]);

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
    } else if (user) {
      // Pre-fill surveyor name for new checklists (if no draft loaded)
      setFormData(prev => prev.surveyor_name ? prev : { ...prev, surveyor_name: user.full_name });
    }
  }, [id, isEdit, user]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleSubmit = async (e, isDraft = false) => {
    e.preventDefault();
    if (!formData.site_name.trim()) {
      setError('Site Name is required');
      return;
    }

    setSaving(true);
    setError(null);

    try {
      // Clean up empty strings to nulls for optional fields
      const cleanData = { ...formData, is_draft: isDraft };
      Object.keys(cleanData).forEach((key) => {
        if (cleanData[key] === '') cleanData[key] = null;
      });

      let finalId = id || draftId;

      if (finalId) {
        // Update existing survey (whether it was a draft or not)
        await checklistApi.update(finalId, cleanData);
      } else {
        // Create new survey
        const response = await checklistApi.create(cleanData);
        finalId = response.data.id;
      }

      // Upload any pending photos
      if (pendingPhotos.length > 0) {
        for (const photo of pendingPhotos) {
          try {
            await checklistApi.uploadPhoto(finalId, photo);
          } catch (photoErr) {
            console.error('Failed to upload photo:', photoErr);
          }
        }
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
    if (!photoFile || !id || photoFile.length === 0) return;
    try {
      let updatedPhotos = formData.site_photos || [];
      for (const file of photoFile) {
        const response = await checklistApi.uploadPhoto(id, file);
        updatedPhotos = response.data.site_photos;
      }
      setFormData((prev) => ({ ...prev, site_photos: updatedPhotos }));
      setPhotoFile(null);
    } catch (err) {
      setError('Failed to upload media');
    }
  };

  if (loading) return <div className="loading">Loading...</div>;

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>{isEdit ? (formData.is_draft ? 'Edit Draft' : 'Edit Checklist') : 'New Site Visit Checklist'}</h2>
        {draftSaved && (
          <span style={{ color: '#27ae60', fontSize: '14px' }}>
            ✓ Draft auto-saved
          </span>
        )}
      </div>

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
                type="text"
                name="building_level"
                value={formData.building_level}
                onChange={handleChange}
              />
            </div>
            <div className="form-group">
              <label>Ceiling Height (meters)</label>
              <input
                type="text"
                name="ceiling_height"
                value={formData.ceiling_height}
                onChange={handleChange}
              />
            </div>
            <div className="form-group">
              <label>Skirting Size</label>
              <input
                type="text"
                name="skirting_size"
                value={formData.skirting_size}
                onChange={handleChange}
              />
            </div>
            <div className="form-group">
              <label>Floor Type</label>
              <input
                type="text"
                name="floor_type"
                value={formData.floor_type}
                onChange={handleChange}
              />
            </div>
            <div className="form-group">
              <label>Soffit Type</label>
              <input
                type="text"
                name="soffit_type"
                value={formData.soffit_type}
                onChange={handleChange}
              />
            </div>
            <div className="form-group">
              <label>Ceiling Type & Trims</label>
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
                type="text"
                name="ceiling_void_depth"
                value={formData.ceiling_void_depth}
                onChange={handleChange}
              />
            </div>
            <div className="form-group">
              <label>Floor Void Depth (mm)</label>
              <input
                type="text"
                name="floor_void_depth"
                value={formData.floor_void_depth}
                onChange={handleChange}
              />
            </div>
          </div>
        </div>

        {/* Access & Logistics */}
        <div className="form-section">
          <h3>Access & Logistics</h3>
          <div className="form-grid">
            <div className="form-group">
              <label>Service Penetrations Scale</label>
              <input
                type="text"
                name="service_penetrations_scale"
                value={formData.service_penetrations_scale}
                onChange={handleChange}
              />
            </div>
            <div className="form-group">
              <div className="checkbox-group">
                <input
                  type="checkbox"
                  name="goods_lift_available"
                  checked={formData.goods_lift_available}
                  onChange={handleChange}
                />
                <label>Goods Lift Available</label>
              </div>
              {formData.goods_lift_available && (
                <input
                  type="text"
                  name="goods_lift_notes"
                  value={formData.goods_lift_notes}
                  onChange={handleChange}
                  placeholder="Add notes..."
                  style={{ marginTop: '8px' }}
                />
              )}
            </div>
            <div className="form-group">
              <div className="checkbox-group">
                <input
                  type="checkbox"
                  name="good_staircase_access"
                  checked={formData.good_staircase_access}
                  onChange={handleChange}
                />
                <label>Good Staircase Access</label>
              </div>
              {formData.good_staircase_access && (
                <input
                  type="text"
                  name="staircase_access_notes"
                  value={formData.staircase_access_notes}
                  onChange={handleChange}
                  placeholder="Add notes..."
                  style={{ marginTop: '8px' }}
                />
              )}
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
            <div className="form-group">
              <div className="checkbox-group">
                <input
                  type="checkbox"
                  name="wall_deflection_needed"
                  checked={formData.wall_deflection_needed}
                  onChange={handleChange}
                />
                <label>Wall Deflection Needed</label>
              </div>
              {formData.wall_deflection_needed && (
                <input
                  type="text"
                  name="wall_deflection_notes"
                  value={formData.wall_deflection_notes}
                  onChange={handleChange}
                  placeholder="Add notes..."
                  style={{ marginTop: '8px' }}
                />
              )}
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
              {formData.door_finish === 'Other' && (
                <input
                  type="text"
                  name="door_finish_other"
                  value={formData.door_finish_other}
                  onChange={handleChange}
                  placeholder="Specify door finish..."
                  style={{ marginTop: '8px' }}
                />
              )}
            </div>
            <div className="form-group">
              <label>Frame Type</label>
              <select name="frame_type" value={formData.frame_type} onChange={handleChange}>
                <option value="">Select...</option>
                <option value="Timber">Timber</option>
                <option value="Metal">Metal</option>
                <option value="Other">Other</option>
              </select>
              {formData.frame_type === 'Other' && (
                <input
                  type="text"
                  name="frame_type_other"
                  value={formData.frame_type_other}
                  onChange={handleChange}
                  placeholder="Specify frame type..."
                  style={{ marginTop: '8px' }}
                />
              )}
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
            <div className="form-group">
              <div className="checkbox-group">
                <input
                  type="checkbox"
                  name="acoustic_baffles_required"
                  checked={formData.acoustic_baffles_required}
                  onChange={handleChange}
                />
                <label>Acoustic Baffles Required</label>
              </div>
              {formData.acoustic_baffles_required && (
                <input
                  type="text"
                  name="acoustic_baffles_notes"
                  value={formData.acoustic_baffles_notes}
                  onChange={handleChange}
                  placeholder="Add notes..."
                  style={{ marginTop: '8px' }}
                />
              )}
            </div>
            <div className="form-group">
              <div className="checkbox-group">
                <input
                  type="checkbox"
                  name="fire_stopping_required"
                  checked={formData.fire_stopping_required}
                  onChange={handleChange}
                />
                <label>Fire Stopping Required</label>
              </div>
              {formData.fire_stopping_required && (
                <input
                  type="text"
                  name="fire_stopping_notes"
                  value={formData.fire_stopping_notes}
                  onChange={handleChange}
                  placeholder="Add notes..."
                  style={{ marginTop: '8px' }}
                />
              )}
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
              <label>Notes</label>
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

          <div className="photo-upload">
            <label>Site Media (Photos & Videos)</label>
            {isEdit ? (
              <>
                <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
                  <input
                    type="file"
                    accept="image/*,video/*"
                    multiple
                    onChange={(e) => {
                      if (e.target.files && e.target.files.length > 0) {
                        setPhotoFile(Array.from(e.target.files));
                      }
                    }}
                  />
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={handlePhotoUpload}
                    disabled={!photoFile || photoFile.length === 0}
                  >
                    Upload Media
                  </button>
                </div>
                {formData.site_photos && formData.site_photos.length > 0 && (
                  <div className="photo-grid">
                    {formData.site_photos.map((media, idx) => {
                      const isVideo = media.match(/\.(mp4|mov|avi|webm|mkv)$/i);
                      return isVideo ? (
                        <video
                          key={idx}
                          src={`${API_BASE}${media}`}
                          controls
                          style={{ maxWidth: '200px', maxHeight: '150px' }}
                        />
                      ) : (
                        <img
                          key={idx}
                          src={`${API_BASE}${media}`}
                          alt={`Site media ${idx + 1}`}
                        />
                      );
                    })}
                  </div>
                )}
              </>
            ) : (
              <>
                <div style={{ marginTop: '10px' }}>
                  {pendingPhotos.length > 0 && (
                    <div style={{ 
                      background: '#d4edda', 
                      border: '1px solid #27ae60',
                      borderRadius: '4px',
                      padding: '10px',
                      marginBottom: '10px',
                      color: '#155724',
                      fontWeight: '500'
                    }}>
                      ✓ {pendingPhotos.length} file(s) selected
                    </div>
                  )}
                  <input
                    type="file"
                    accept="image/*,video/*"
                    multiple
                    onChange={(e) => {
                      console.log('[FILE INPUT] onChange fired, files:', e.target.files?.length || 0);
                      if (e.target.files && e.target.files.length > 0) {
                        const files = Array.from(e.target.files);
                        console.log('[FILE INPUT] Adding files:', files.map(f => f.name));
                        setPendingPhotos(prev => {
                          const updated = [...prev, ...files];
                          console.log('[FILE INPUT] Updated pendingPhotos count:', updated.length);
                          return updated;
                        });
                        e.target.value = ''; // Reset input to allow selecting same file
                      }
                    }}
                    style={{ display: 'block', marginBottom: '8px' }}
                  />
                  {pendingPhotos.length === 0 && (
                    <span style={{ color: '#666', fontSize: '14px', display: 'block' }}>
                      Tap "Choose Files" above to select photos/videos
                    </span>
                  )}
                </div>
                {pendingPhotos.length > 0 && (
                  <>
                    <div style={{ marginTop: '15px', marginBottom: '10px' }}>
                      <strong>Selected files:</strong>
                      <ul style={{ marginTop: '5px', paddingLeft: '20px', fontSize: '14px', color: '#555' }}>
                        {pendingPhotos.map((media, idx) => (
                          <li key={idx} style={{ marginBottom: '4px' }}>
                            {media.name} ({(media.size / 1024).toFixed(1)} KB)
                            <button
                              type="button"
                              onClick={() => setPendingPhotos(prev => prev.filter((_, i) => i !== idx))}
                              style={{
                                marginLeft: '10px',
                                background: '#e74c3c',
                                color: 'white',
                                border: 'none',
                                borderRadius: '4px',
                                padding: '2px 8px',
                                cursor: 'pointer',
                                fontSize: '12px'
                              }}
                            >
                              Remove
                            </button>
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div className="photo-grid" style={{ marginTop: '10px' }}>
                      {pendingPhotos.map((media, idx) => {
                        const isVideo = media.type.startsWith('video/');
                        return (
                          <div key={idx} style={{ position: 'relative' }}>
                            {isVideo ? (
                              <video
                                src={URL.createObjectURL(media)}
                                controls
                                style={{ maxWidth: '200px', maxHeight: '150px' }}
                              />
                            ) : (
                              <img
                                src={URL.createObjectURL(media)}
                                alt={`Pending media ${idx + 1}`}
                              />
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </>
                )}
              </>
            )}
          </div>
        </div>

        <div className="form-actions">
          <button type="submit" className="btn btn-success" disabled={saving}>
            {saving ? 'Submitting...' : (isEdit || draftId ? 'Submit Survey' : 'Submit Survey')}
          </button>
          <button type="button" className="btn btn-secondary" onClick={() => navigate('/')}>
            Cancel
          </button>
          {(isEdit || draftId) && (
            <p style={{ fontSize: '14px', color: '#666', marginTop: '10px', marginBottom: 0 }}>
              Draft auto-saves as you type. Click "Submit Survey" when ready to finalize.
            </p>
          )}
        </div>
      </form>
    </div>
  );
}

export default ChecklistForm;
