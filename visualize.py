#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ויזואליזציה של נתוני מטופלות
"""

import pandas as pd
import json
import matplotlib.pyplot as plt
import matplotlib
from datetime import datetime

# הגדרת פונט לתמיכה בעברית
matplotlib.rcParams['font.family'] = 'DejaVu Sans'

# קריאת הנתונים המאוחדים
with open('output/merged_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# יצירת DataFrame
df = pd.DataFrame(data['patients'])
df['date'] = pd.to_datetime(df['date'])
df['year_month'] = df['date'].dt.to_period('M').astype(str)

# ספירת מטופלות לפי חודש
monthly_counts = df.groupby('year_month').size().reset_index(name='count')

print("="*60)
print("📈 ניתוח פעילות לפי חודשים")
print("="*60)
print()

for _, row in monthly_counts.iterrows():
    bar = "█" * row['count']
    print(f"{row['year_month']}: {bar} ({row['count']})")

print()
print("="*60)
print("📊 סטטיסטיקות טיפולים")
print("="*60)
print()

# טיפולים נפוצים
treatment_counts = df['treatment'].value_counts()
print("סוגי טיפול נפוצים:")
for treatment, count in treatment_counts.items():
    print(f"   • {treatment}: {count} מטופלים")

print()

# אבחנות נפוצות
diagnosis_counts = df['diagnosis'].value_counts()
print("אבחנות נפוצות:")
for diagnosis, count in diagnosis_counts.head(5).items():
    print(f"   • {diagnosis}: {count} מקרים")

print()

# התפלגות גילאים
print(f"התפלגות גילאים:")
print(f"   • גיל ממוצע: {df['age'].mean():.1f}")
print(f"   • טווח: {df['age'].min()} - {df['age'].max()}")

print()

# סך טיפולים
total_sessions = df['sessions'].sum()
print(f"סה\"כ טיפולים שניתנו: {total_sessions}")

print()
print("="*60)

# שמירת גרף
plt.figure(figsize=(12, 6))
plt.bar(monthly_counts['year_month'], monthly_counts['count'], color='#4A90E2')
plt.xlabel('Month-Year', fontsize=12)
plt.ylabel('Number of Patients', fontsize=12)
plt.title('Patient Activity Over Time', fontsize=14, fontweight='bold')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('output/activity_timeline.png', dpi=150)
print("📊 גרף נשמר ב: output/activity_timeline.png")
print("="*60)
