import { LetterTemplate } from '../types/patient';

export const letterTemplates: LetterTemplate[] = [
  {
    id: 'referral-specialist',
    name: 'Specialist Referral',
    nameHebrew: 'הפניה לרופא מומחה',
    description: 'הפניה לרופא מומחה לבדיקה או טיפול',
    category: 'referral',
    content: `לכבוד
ד"ר _____________
מומחה ב_____________

הנדון: הפניית מטופל/ת

מטופל/ת יקר/ה {{patientFullName}} ת.ז. {{patientId}}
נולד/ה בתאריך {{patientDOB}}

אני מפנה אליך את המטופל/ת הנ"ל לצורך:
{{customContent}}

אודה לך על בדיקתך וחוות דעתך.

בברכה,
{{doctorName}}
מס' רישיון: {{licenseNumber}}`
  },
  {
    id: 'visit-summary',
    name: 'Visit Summary',
    nameHebrew: 'סיכום ביקור',
    description: 'סיכום ביקור במרפאה',
    category: 'summary',
    content: `סיכום ביקור

פרטי המטופל/ת:
שם: {{patientFullName}}
ת.ז.: {{patientId}}
תאריך לידה: {{patientDOB}}
כתובת: {{patientAddress}}
טלפון: {{patientPhone}}

תאריך הביקור: {{date}}

תלונות ומהלך הביקור:
{{customContent}}

המלצות:
_____________________________________________
_____________________________________________

בברכה,
{{doctorName}}
מס' רישיון: {{licenseNumber}}
{{clinicName}}
{{clinicAddress}}
טל: {{clinicPhone}}`
  },
  {
    id: 'medical-certificate',
    name: 'Medical Certificate',
    nameHebrew: 'אישור רפואי',
    description: 'אישור רפואי כללי',
    category: 'certificate',
    content: `אישור רפואי

אני הח"מ, {{doctorName}}, מס' רישיון {{licenseNumber}},
מאשר/ת בזאת כי:

{{patientFullName}}
ת.ז. {{patientId}}
נולד/ה: {{patientDOB}}

{{customContent}}

אישור זה ניתן לבקשת המטופל/ת.

תאריך: {{date}}

חתימה וחותמת:
{{doctorName}}
{{clinicName}}
{{clinicAddress}}`
  },
  {
    id: 'sick-leave',
    name: 'Sick Leave Certificate',
    nameHebrew: 'אישור מחלה',
    description: 'אישור ימי מחלה',
    category: 'certificate',
    content: `אישור מחלה

לכבוד
מחלקת משאבי אנוש

הנדון: אישור מחלה

אני הח"מ, {{doctorName}}, מס' רישיון {{licenseNumber}},
מאשר/ת בזאת כי:

{{patientFullName}}
ת.ז. {{patientId}}

נבדק/ה במרפאתי ונמצא/ה כי אינו/ה מסוגל/ת לעבוד
מתאריך: _____________
עד תאריך: _____________

{{customContent}}

תאריך הנפקת האישור: {{date}}

חתימה וחותמת:
{{doctorName}}
{{clinicName}}`
  },
  {
    id: 'prescription',
    name: 'Prescription Letter',
    nameHebrew: 'מכתב מרשם',
    description: 'מכתב נלווה למרשם',
    category: 'prescription',
    content: `מכתב נלווה למרשם

פרטי המטופל/ת:
שם: {{patientFullName}}
ת.ז.: {{patientId}}
תאריך לידה: {{patientDOB}}
קופת חולים: {{healthFund}}

תאריך: {{date}}

להלן הנחיות לשימוש בתרופות:
{{customContent}}

הערות חשובות:
• יש לעקוב אחר ההוראות בדייקנות
• במקרה של תופעות לוואי יש לפנות מיידית לרופא
• יש לשמור תרופות הרחק מהישג ידם של ילדים

בברכת רפואה שלמה,
{{doctorName}}
מס' רישיון: {{licenseNumber}}
{{clinicName}}
טל: {{clinicPhone}}`
  },
  {
    id: 'general-letter',
    name: 'General Letter',
    nameHebrew: 'מכתב כללי',
    description: 'מכתב כללי למטופל/ת',
    category: 'general',
    content: `תאריך: {{date}}

לכבוד
{{patientFullName}}
{{patientAddress}}

שלום רב,

{{customContent}}

בברכה,
{{doctorName}}
{{clinicName}}
{{clinicAddress}}
טל: {{clinicPhone}}`
  },
  {
    id: 'lab-referral',
    name: 'Lab Test Referral',
    nameHebrew: 'הפניה לבדיקות מעבדה',
    description: 'הפניה לביצוע בדיקות מעבדה',
    category: 'referral',
    content: `הפניה לבדיקות מעבדה

פרטי המטופל/ת:
שם: {{patientFullName}}
ת.ז.: {{patientId}}
תאריך לידה: {{patientDOB}}
קופת חולים: {{healthFund}}
טלפון: {{patientPhone}}

תאריך ההפניה: {{date}}

בדיקות נדרשות:
{{customContent}}

הערות קליניות:
_____________________________________________

הנחיות למטופל/ת:
• יש להגיע לבדיקות בצום (אם נדרש)
• יש להביא הפניה זו וכרטיס קופת חולים
• יש לציין בפני הצוות הרפואי על תרופות קבועות

{{doctorName}}
מס' רישיון: {{licenseNumber}}
{{clinicName}}`
  },
  {
    id: 'imaging-referral',
    name: 'Imaging Referral',
    nameHebrew: 'הפניה לבדיקות הדמיה',
    description: 'הפניה לבדיקות הדמיה (רנטגן, CT, MRI וכו\')',
    category: 'referral',
    content: `הפניה לבדיקות הדמיה

פרטי המטופל/ת:
שם: {{patientFullName}}
ת.ז.: {{patientId}}
תאריך לידה: {{patientDOB}}
קופת חולים: {{healthFund}}

תאריך ההפניה: {{date}}

סוג הבדיקה הנדרשת:
{{customContent}}

אזור הבדיקה: _____________
צד: ימין / שמאל / דו-צדדי

רקע קליני והתוויה:
_____________________________________________
_____________________________________________

האם קיימת הריון? כן / לא / לא ידוע
אלרגיות ידועות: _____________

{{doctorName}}
מס' רישיון: {{licenseNumber}}
{{clinicName}}
טל: {{clinicPhone}}`
  }
];

export const getTemplatesByCategory = (category: string): LetterTemplate[] => {
  return letterTemplates.filter(t => t.category === category);
};

export const getTemplateById = (id: string): LetterTemplate | undefined => {
  return letterTemplates.find(t => t.id === id);
};

export const categoryLabels: Record<string, string> = {
  referral: 'הפניות',
  summary: 'סיכומים',
  prescription: 'מרשמים',
  certificate: 'אישורים',
  general: 'כללי'
};
