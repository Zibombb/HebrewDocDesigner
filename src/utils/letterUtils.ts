import { LetterData, Patient } from '../types/patient';

export const formatDate = (dateString: string): string => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('he-IL', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
};

export const formatShortDate = (dateString: string): string => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('he-IL');
};

export const getPatientFullName = (patient: Patient): string => {
  return `${patient.firstName} ${patient.lastName}`;
};

export const getPatientAddress = (patient: Patient): string => {
  const { street, city, zipCode } = patient.address;
  let address = `${street}, ${city}`;
  if (zipCode) {
    address += ` ${zipCode}`;
  }
  return address;
};

export const renderLetter = (data: LetterData): string => {
  let content = data.template.content;

  const replacements: Record<string, string> = {
    '{{patientFullName}}': getPatientFullName(data.patient),
    '{{patientId}}': data.patient.idNumber,
    '{{patientDOB}}': formatShortDate(data.patient.dateOfBirth),
    '{{patientPhone}}': data.patient.phone,
    '{{patientEmail}}': data.patient.email || '',
    '{{patientAddress}}': getPatientAddress(data.patient),
    '{{healthFund}}': data.patient.healthFund || '_____________',
    '{{date}}': formatDate(data.date),
    '{{doctorName}}': data.doctorName,
    '{{clinicName}}': data.clinicName,
    '{{clinicAddress}}': data.clinicAddress,
    '{{clinicPhone}}': data.clinicPhone,
    '{{licenseNumber}}': data.licenseNumber,
    '{{customContent}}': data.customContent || '_____________________________________________'
  };

  for (const [placeholder, value] of Object.entries(replacements)) {
    content = content.replace(new RegExp(placeholder.replace(/[{}]/g, '\\$&'), 'g'), value);
  }

  return content;
};

export const generateId = (): string => {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

export const validateIsraeliId = (id: string): boolean => {
  if (!/^\d{9}$/.test(id)) return false;

  const digits = id.split('').map(Number);
  const sum = digits.reduce((acc, digit, index) => {
    let val = digit * ((index % 2) + 1);
    if (val > 9) val -= 9;
    return acc + val;
  }, 0);

  return sum % 10 === 0;
};

export const validatePhone = (phone: string): boolean => {
  const cleanPhone = phone.replace(/[-\s]/g, '');
  return /^0[2-9]\d{7,8}$/.test(cleanPhone);
};

export const validateEmail = (email: string): boolean => {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
};
