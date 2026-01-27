import React from 'react';
import { Patient } from '../types/patient';
import './PatientForm.css';

interface PatientFormProps {
  patient: Patient;
  onChange: (patient: Patient) => void;
}

export const PatientForm: React.FC<PatientFormProps> = ({ patient, onChange }) => {
  const handleChange = (field: string, value: string) => {
    if (field.startsWith('address.')) {
      const addressField = field.replace('address.', '');
      onChange({
        ...patient,
        address: {
          ...patient.address,
          [addressField]: value
        }
      });
    } else {
      onChange({
        ...patient,
        [field]: value
      });
    }
  };

  return (
    <div className="patient-form">
      <h3 className="form-section-title">פרטי מטופל/ת</h3>

      <div className="form-row">
        <div className="form-group">
          <label className="form-label">שם פרטי *</label>
          <input
            type="text"
            className="form-input"
            value={patient.firstName}
            onChange={(e) => handleChange('firstName', e.target.value)}
            placeholder="הכנס שם פרטי"
          />
        </div>
        <div className="form-group">
          <label className="form-label">שם משפחה *</label>
          <input
            type="text"
            className="form-input"
            value={patient.lastName}
            onChange={(e) => handleChange('lastName', e.target.value)}
            placeholder="הכנס שם משפחה"
          />
        </div>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label className="form-label">תעודת זהות *</label>
          <input
            type="text"
            className="form-input"
            value={patient.idNumber}
            onChange={(e) => handleChange('idNumber', e.target.value)}
            placeholder="000000000"
            maxLength={9}
          />
        </div>
        <div className="form-group">
          <label className="form-label">תאריך לידה *</label>
          <input
            type="date"
            className="form-input"
            value={patient.dateOfBirth}
            onChange={(e) => handleChange('dateOfBirth', e.target.value)}
          />
        </div>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label className="form-label">טלפון *</label>
          <input
            type="tel"
            className="form-input"
            value={patient.phone}
            onChange={(e) => handleChange('phone', e.target.value)}
            placeholder="050-0000000"
          />
        </div>
        <div className="form-group">
          <label className="form-label">דוא"ל</label>
          <input
            type="email"
            className="form-input"
            value={patient.email || ''}
            onChange={(e) => handleChange('email', e.target.value)}
            placeholder="email@example.com"
          />
        </div>
      </div>

      <h4 className="form-subsection-title">כתובת</h4>

      <div className="form-row">
        <div className="form-group flex-2">
          <label className="form-label">רחוב ומספר *</label>
          <input
            type="text"
            className="form-input"
            value={patient.address.street}
            onChange={(e) => handleChange('address.street', e.target.value)}
            placeholder="שם הרחוב ומספר בית"
          />
        </div>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label className="form-label">עיר *</label>
          <input
            type="text"
            className="form-input"
            value={patient.address.city}
            onChange={(e) => handleChange('address.city', e.target.value)}
            placeholder="שם העיר"
          />
        </div>
        <div className="form-group">
          <label className="form-label">מיקוד</label>
          <input
            type="text"
            className="form-input"
            value={patient.address.zipCode || ''}
            onChange={(e) => handleChange('address.zipCode', e.target.value)}
            placeholder="0000000"
            maxLength={7}
          />
        </div>
      </div>

      <h4 className="form-subsection-title">מידע נוסף</h4>

      <div className="form-group">
        <label className="form-label">קופת חולים</label>
        <select
          className="form-input"
          value={patient.healthFund || ''}
          onChange={(e) => handleChange('healthFund', e.target.value)}
        >
          <option value="">בחר קופת חולים</option>
          <option value="כללית">כללית</option>
          <option value="מכבי">מכבי</option>
          <option value="מאוחדת">מאוחדת</option>
          <option value="לאומית">לאומית</option>
          <option value="אחר">אחר</option>
        </select>
      </div>
    </div>
  );
};
