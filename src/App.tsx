import { useState, useCallback } from 'react';
import { Patient, LetterTemplate, LetterData } from './types/patient';
import { PatientForm } from './components/PatientForm';
import { TemplateSelector } from './components/TemplateSelector';
import { LetterPreview } from './components/LetterPreview';
import { ClinicSettings } from './components/ClinicSettings';
import { generateId } from './utils/letterUtils';
import './App.css';

const initialPatient: Patient = {
  id: generateId(),
  firstName: '',
  lastName: '',
  idNumber: '',
  dateOfBirth: '',
  phone: '',
  email: '',
  address: {
    street: '',
    city: '',
    zipCode: ''
  },
  healthFund: ''
};

const initialClinicData = {
  doctorName: '',
  licenseNumber: '',
  clinicName: '',
  clinicAddress: '',
  clinicPhone: ''
};

function App() {
  const [patient, setPatient] = useState<Patient>(initialPatient);
  const [selectedTemplate, setSelectedTemplate] = useState<LetterTemplate | null>(null);
  const [customContent, setCustomContent] = useState('');
  const [clinicData, setClinicData] = useState(initialClinicData);
  const [isClinicSettingsExpanded, setIsClinicSettingsExpanded] = useState(true);

  const letterData: LetterData | null = selectedTemplate ? {
    patient,
    template: selectedTemplate,
    customContent,
    date: new Date().toISOString().split('T')[0],
    ...clinicData
  } : null;

  const handlePrint = useCallback(() => {
    window.print();
  }, []);

  const handleReset = useCallback(() => {
    setPatient({ ...initialPatient, id: generateId() });
    setSelectedTemplate(null);
    setCustomContent('');
  }, []);

  return (
    <div className="app">
      <header className="app-header no-print">
        <div className="header-content">
          <h1 className="app-title">
            <span className="title-icon">📋</span>
            מעצב מסמכים - מכתבים למטופלות
          </h1>
          <p className="app-subtitle">יצירת מכתבים רפואיים בעברית</p>
        </div>
        <button className="btn btn-secondary" onClick={handleReset}>
          התחל מחדש
        </button>
      </header>

      <main className="app-main">
        <div className="app-layout">
          <aside className="sidebar no-print">
            <ClinicSettings
              clinicData={clinicData}
              onChange={setClinicData}
              isExpanded={isClinicSettingsExpanded}
              onToggle={() => setIsClinicSettingsExpanded(!isClinicSettingsExpanded)}
            />

            <PatientForm
              patient={patient}
              onChange={setPatient}
            />

            <TemplateSelector
              selectedTemplate={selectedTemplate}
              onSelect={setSelectedTemplate}
            />
          </aside>

          <section className="main-content">
            <LetterPreview
              letterData={letterData}
              customContent={customContent}
              onCustomContentChange={setCustomContent}
              onPrint={handlePrint}
            />
          </section>
        </div>
      </main>

      <footer className="app-footer no-print">
        <p>מעצב מסמכים - מכתבים למטופלות | כל הזכויות שמורות &copy; {new Date().getFullYear()}</p>
      </footer>
    </div>
  );
}

export default App;
