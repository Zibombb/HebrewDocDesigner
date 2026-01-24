#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
בדיקת המערכת - Test script
"""

from data_processor import PatientDataProcessor
import json

# יצירת מעבד
processor = PatientDataProcessor()

# רשימת קבצים לעיבוד
files = [
    'data/example_patients_2023.json',
    'data/example_patients_2024.json'
]

print("="*60)
print("🏥 מערכת ניתוח נתוני מטופלות - בדיקה")
print("="*60)
print()

# עיבוד הקבצים
results = processor.process_files(files)

if 'error' in results:
    print(f"❌ שגיאה: {results['error']}")
else:
    print("✅ הקבצים עובדו בהצלחה!")
    print()

    # סטטיסטיקות
    stats = results['statistics']
    print("📊 סטטיסטיקות כלליות:")
    print(f"   • סך הכל מטופלות: {stats['total_patients']}")
    print(f"   • כפולים שנמצאו: {results['duplicates_found']}")
    print(f"   • קבוצות שמות דומים: {results['similar_names_groups']}")
    print(f"   • שדות במערכת: {len(stats['columns'])}")
    print()

    # טווח תאריכים
    if 'date_range' in stats and stats['date_range']['earliest']:
        print("📅 טווח תאריכים:")
        print(f"   • מוקדם ביותר: {stats['date_range']['earliest'][:10]}")
        print(f"   • מאוחר ביותר: {stats['date_range']['latest'][:10]}")
        print()

    # כפולים
    if results['duplicates_found'] > 0:
        print("⚠️  רשומות כפולות:")
        for i, dup in enumerate(results['duplicates']):
            orig = dup['original']
            dup_rec = dup['duplicate']
            print(f"   {i+1}. {orig.get('name', 'ללא שם')} - {orig.get('date', 'ללא תאריך')}")
            print(f"      vs {dup_rec.get('name', 'ללא שם')} - {dup_rec.get('date', 'ללא תאריך')}")
        print()

    # שמות דומים
    if results['similar_names_groups'] > 0:
        print("👥 קבוצות שמות דומים:")
        for i, group in enumerate(results['similar_names']):
            print(f"   קבוצה {i+1}:")
            for item in group['group']:
                print(f"      • {item['name']}")
        print()

    # נתונים בסיסיים
    print("📋 השדות במערכת:")
    print(f"   {', '.join(stats['columns'])}")
    print()

    # תצוגת כמה רשומות
    df = results['dataframe']
    print("📝 דוגמה - 5 רשומות ראשונות:")
    print()

    # הדפסה מעוצבת
    for idx, row in df.head(5).iterrows():
        print(f"   {idx+1}. {row.get('name', 'ללא שם')}")
        print(f"      תאריך: {row.get('date', 'ללא תאריך')}")
        print(f"      גיל: {row.get('age', 'לא צוין')}")
        print(f"      אבחנה: {row.get('diagnosis', 'לא צוין')}")
        print()

    print("="*60)
    print(f"💾 נתונים מאוחדים נשמרו ב: {results['output_file']}")
    print("="*60)
