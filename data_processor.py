#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
מעבד נתוני מטופלות - Data Processor for Patient Records
עיבוד, איחוד וניתוח נתוני מטופלות ממרפאת כאבי גב
"""

import json
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple
from difflib import SequenceMatcher
import Levenshtein


class PatientDataProcessor:
    """מעבד נתונים למטופלות"""

    def __init__(self, data_dir: str = "data", output_dir: str = "output"):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)

    def load_json_files(self, file_paths: List[str]) -> List[Dict]:
        """טעינת קבצי JSON"""
        all_records = []

        for file_path in file_paths:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # תמיכה בפורמטים שונים
                    if isinstance(data, list):
                        all_records.extend(data)
                    elif isinstance(data, dict):
                        # אם זה אובייקט בודד, נוסיף אותו כרשומה
                        if 'patients' in data:
                            all_records.extend(data['patients'])
                        elif 'records' in data:
                            all_records.extend(data['records'])
                        else:
                            all_records.append(data)
            except Exception as e:
                print(f"שגיאה בטעינת קובץ {file_path}: {e}")

        return all_records

    def normalize_name(self, name: str) -> str:
        """נרמול שמות למניעת כפילויות"""
        if not name:
            return ""
        # הסרת רווחים מיותרים, המרה לאותיות קטנות
        return ' '.join(name.strip().split()).lower()

    def calculate_name_similarity(self, name1: str, name2: str) -> float:
        """חישוב דמיון בין שמות"""
        if not name1 or not name2:
            return 0.0

        # שימוש באלגוריתם Levenshtein לחישוב מרחק
        similarity = Levenshtein.ratio(
            self.normalize_name(name1),
            self.normalize_name(name2)
        )
        return similarity

    def find_duplicates(self, records: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """זיהוי רשומות כפולות"""
        seen = {}
        duplicates = []
        unique_records = []

        for record in records:
            # נשתמש בשילוב של שם ותאריך לזיהוי
            name = record.get('name', record.get('שם', ''))
            date = record.get('date', record.get('תאריך', ''))

            # יצירת מפתח ייחודי
            key = f"{self.normalize_name(name)}_{date}"

            if key in seen:
                duplicates.append({
                    'original': seen[key],
                    'duplicate': record
                })
            else:
                seen[key] = record
                unique_records.append(record)

        return unique_records, duplicates

    def find_similar_names(self, records: List[Dict], threshold: float = 0.85) -> List[Dict]:
        """מציאת שמות דומים שעלולים להיות אותה מטופלת"""
        similar_groups = []
        names = [(i, record.get('name', record.get('שם', '')))
                for i, record in enumerate(records)]

        checked = set()

        for i, name1 in names:
            if i in checked:
                continue

            group = [{'index': i, 'name': name1, 'record': records[i]}]

            for j, name2 in names[i+1:]:
                if j in checked:
                    continue

                similarity = self.calculate_name_similarity(name1, name2)
                if similarity >= threshold:
                    group.append({'index': j, 'name': name2, 'record': records[j]})
                    checked.add(j)

            if len(group) > 1:
                similar_groups.append({
                    'similarity_score': threshold,
                    'group': group
                })
                checked.add(i)

        return similar_groups

    def merge_records(self, records: List[Dict]) -> Dict:
        """איחוד רשומות למבנה אחד"""
        merged_data = {
            'metadata': {
                'total_records': len(records),
                'merge_date': datetime.now().isoformat(),
                'source_files_count': 0
            },
            'patients': records
        }

        return merged_data

    def create_dataframe(self, records: List[Dict]) -> pd.DataFrame:
        """יצירת DataFrame לניתוח"""
        df = pd.DataFrame(records)

        # נסה לזהות עמודת תאריך
        date_columns = ['date', 'תאריך', 'visit_date', 'תאריך_ביקור']
        for col in date_columns:
            if col in df.columns:
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                except:
                    pass

        return df

    def generate_statistics(self, df: pd.DataFrame) -> Dict:
        """יצירת סטטיסטיקות"""
        stats = {
            'total_patients': len(df),
            'columns': list(df.columns),
            'missing_data': df.isnull().sum().to_dict(),
        }

        # זיהוי עמודות תאריך
        date_cols = df.select_dtypes(include=['datetime64']).columns
        if len(date_cols) > 0:
            date_col = date_cols[0]
            stats['date_range'] = {
                'earliest': df[date_col].min().isoformat() if pd.notna(df[date_col].min()) else None,
                'latest': df[date_col].max().isoformat() if pd.notna(df[date_col].max()) else None
            }

        return stats

    def save_merged_data(self, data: Dict, filename: str = "merged_data.json"):
        """שמירת נתונים מאוחדים"""
        output_path = self.output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return output_path

    def process_files(self, file_paths: List[str]) -> Dict:
        """עיבוד מלא של קבצים"""
        # טעינת נתונים
        records = self.load_json_files(file_paths)

        if not records:
            return {'error': 'לא נמצאו רשומות'}

        # זיהוי כפולים
        unique_records, duplicates = self.find_duplicates(records)

        # מציאת שמות דומים
        similar_names = self.find_similar_names(unique_records)

        # יצירת DataFrame
        df = self.create_dataframe(unique_records)

        # סטטיסטיקות
        stats = self.generate_statistics(df)

        # איחוד נתונים
        merged_data = self.merge_records(unique_records)
        merged_data['metadata']['source_files_count'] = len(file_paths)

        # שמירה
        output_path = self.save_merged_data(merged_data)

        return {
            'success': True,
            'output_file': str(output_path),
            'statistics': stats,
            'duplicates_found': len(duplicates),
            'duplicates': duplicates,
            'similar_names_groups': len(similar_names),
            'similar_names': similar_names,
            'dataframe': df
        }


if __name__ == "__main__":
    processor = PatientDataProcessor()
    print("מעבד נתוני מטופלות - מוכן לשימוש")
