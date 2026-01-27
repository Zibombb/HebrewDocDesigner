import React from 'react';
import './ClinicSettings.css';

interface ClinicData {
  doctorName: string;
  licenseNumber: string;
  clinicName: string;
  clinicAddress: string;
  clinicPhone: string;
}

interface ClinicSettingsProps {
  clinicData: ClinicData;
  onChange: (data: ClinicData) => void;
  isExpanded: boolean;
  onToggle: () => void;
}

export const ClinicSettings: React.FC<ClinicSettingsProps> = ({
  clinicData,
  onChange,
  isExpanded,
  onToggle
}) => {
  const handleChange = (field: keyof ClinicData, value: string) => {
    onChange({
      ...clinicData,
      [field]: value
    });
  };

  return (
    <div className="clinic-settings">
      <button className="clinic-settings-toggle" onClick={onToggle}>
        <span className="toggle-icon">{isExpanded ? '▼' : '◀'}</span>
        <span className="toggle-text">הגדרות מרפאה ורופא/ה</span>
        {!isExpanded && clinicData.doctorName && (
          <span className="toggle-preview">({clinicData.doctorName})</span>
        )}
      </button>

      {isExpanded && (
        <div className="clinic-settings-content">
          <div className="form-row">
            <div className="form-group">
              <label className="form-label">שם הרופא/ה *</label>
              <input
                type="text"
                className="form-input"
                value={clinicData.doctorName}
                onChange={(e) => handleChange('doctorName', e.target.value)}
                placeholder='ד"ר ישראל ישראלי'
              />
            </div>
            <div className="form-group">
              <label className="form-label">מספר רישיון *</label>
              <input
                type="text"
                className="form-input"
                value={clinicData.licenseNumber}
                onChange={(e) => handleChange('licenseNumber', e.target.value)}
                placeholder="00000"
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">שם המרפאה *</label>
            <input
              type="text"
              className="form-input"
              value={clinicData.clinicName}
              onChange={(e) => handleChange('clinicName', e.target.value)}
              placeholder="שם המרפאה או המוסד הרפואי"
            />
          </div>

          <div className="form-group">
            <label className="form-label">כתובת המרפאה *</label>
            <input
              type="text"
              className="form-input"
              value={clinicData.clinicAddress}
              onChange={(e) => handleChange('clinicAddress', e.target.value)}
              placeholder="רחוב, מספר, עיר"
            />
          </div>

          <div className="form-group">
            <label className="form-label">טלפון המרפאה *</label>
            <input
              type="tel"
              className="form-input"
              value={clinicData.clinicPhone}
              onChange={(e) => handleChange('clinicPhone', e.target.value)}
              placeholder="03-0000000"
            />
          </div>
        </div>
      )}
    </div>
  );
};
