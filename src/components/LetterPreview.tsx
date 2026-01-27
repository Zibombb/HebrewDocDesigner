import React from 'react';
import { LetterData } from '../types/patient';
import { renderLetter, formatDate } from '../utils/letterUtils';
import './LetterPreview.css';

interface LetterPreviewProps {
  letterData: LetterData | null;
  customContent: string;
  onCustomContentChange: (content: string) => void;
  onPrint: () => void;
}

export const LetterPreview: React.FC<LetterPreviewProps> = ({
  letterData,
  customContent,
  onCustomContentChange,
  onPrint
}) => {
  if (!letterData) {
    return (
      <div className="letter-preview-container">
        <div className="letter-preview-empty">
          <div className="empty-icon">📄</div>
          <h3>בחר תבנית מכתב</h3>
          <p>בחר תבנית מהרשימה ומלא את פרטי המטופל/ת כדי ליצור מכתב</p>
        </div>
      </div>
    );
  }

  const renderedContent = renderLetter({
    ...letterData,
    customContent
  });

  return (
    <div className="letter-preview-container">
      <div className="preview-header no-print">
        <h3 className="preview-title">תצוגה מקדימה</h3>
        <div className="preview-actions">
          <button className="btn btn-primary" onClick={onPrint}>
            <span className="btn-icon">🖨️</span>
            הדפס מכתב
          </button>
        </div>
      </div>

      <div className="custom-content-section no-print">
        <label className="form-label">תוכן מותאם אישית</label>
        <textarea
          className="form-input form-textarea"
          value={customContent}
          onChange={(e) => onCustomContentChange(e.target.value)}
          placeholder="הזן כאן את התוכן המותאם אישית למכתב..."
          rows={4}
        />
      </div>

      <div className="letter-preview" id="letter-to-print">
        <div className="letter-header">
          <div className="clinic-info">
            <h2 className="clinic-name">{letterData.clinicName}</h2>
            <p>{letterData.clinicAddress}</p>
            <p>טל: {letterData.clinicPhone}</p>
          </div>
          <div className="letter-date">
            {formatDate(letterData.date)}
          </div>
        </div>

        <div className="letter-content">
          {renderedContent.split('\n').map((line, index) => (
            <p key={index} className={line.trim() === '' ? 'empty-line' : ''}>
              {line || '\u00A0'}
            </p>
          ))}
        </div>

        <div className="letter-footer">
          <div className="signature-area">
            <div className="signature-line"></div>
            <p>חתימה וחותמת</p>
          </div>
        </div>
      </div>
    </div>
  );
};
