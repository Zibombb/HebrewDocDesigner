export interface Patient {
  id: string;
  firstName: string;
  lastName: string;
  idNumber: string;
  dateOfBirth: string;
  phone: string;
  email?: string;
  address: Address;
  healthFund?: string;
  medicalInfo?: MedicalInfo;
}

export interface Address {
  street: string;
  city: string;
  zipCode?: string;
}

export interface MedicalInfo {
  lastVisit?: string;
  diagnosis?: string;
  treatments?: string[];
  notes?: string;
}

export interface LetterData {
  patient: Patient;
  template: LetterTemplate;
  customContent?: string;
  date: string;
  doctorName: string;
  clinicName: string;
  clinicAddress: string;
  clinicPhone: string;
  licenseNumber: string;
}

export interface LetterTemplate {
  id: string;
  name: string;
  nameHebrew: string;
  description: string;
  content: string;
  category: LetterCategory;
}

export type LetterCategory =
  | 'referral'      // הפניה
  | 'summary'       // סיכום ביקור
  | 'prescription'  // מרשם
  | 'certificate'   // אישור
  | 'general';      // כללי
